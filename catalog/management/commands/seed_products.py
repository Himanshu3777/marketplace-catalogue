"""Seed the catalogue with original/synthetic data.

Usage:
    python manage.py seed_products
    python manage.py seed_products --products 5000
    python manage.py seed_products --products 50000 --batch 2000
    python manage.py seed_products --categories 30
"""
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from catalog.data import pools
from catalog.data import pools2  # noqa: F401
from catalog.data import pools3  # noqa: F401
from catalog.data.generator import CatalogueGenerator, SELLERS
from catalog.models import (
    Brand, Category, Product, ProductImage, ProductSpecification,
    ProductVariant, SubCategory,
)
from inventory.models import Inventory, Price
from reviews.models import ProductReview
from sellers.models import Seller


class Command(BaseCommand):
    help = "Seed synthetic catalogue data (original, development-only)."

    def add_arguments(self, parser):
        parser.add_argument("--categories", type=int, default=30)
        parser.add_argument("--products", type=int, default=5000)
        parser.add_argument("--batch", type=int, default=1000,
                            help="bulk_create batch size")
        parser.add_argument("--seed", type=int, default=42)

    def handle(self, *args, **opts):
        n_cats = opts["categories"]
        n_products = opts["products"]
        batch = opts["batch"]
        gen = CatalogueGenerator(seed=opts["seed"])

        self.stdout.write("Seeding reference data (categories, brands, sellers)...")
        cat_map, sub_map, brand_map, seller_map = self._seed_reference(n_cats, gen)

        self.stdout.write(f"Generating {n_products} products...")
        created = 0
        with transaction.atomic():
            buf = []
            for p in gen.iter_products(n_products):
                buf.append(p)
                if len(buf) >= batch:
                    created += self._insert_batch(buf, cat_map, sub_map, brand_map, seller_map)
                    buf = []
                    self.stdout.write(f"  ... {created} products")
            if buf:
                created += self._insert_batch(buf, cat_map, sub_map, brand_map, seller_map)
        self.stdout.write(self.style.SUCCESS(f"Done. {created} products seeded."))

    # ---------- reference data ----------
    def _seed_reference(self, n_cats, gen):
        cat_map, sub_map = {}, {}
        for i, (cname, cdesc, subcats) in enumerate(pools.CATEGORIES[:n_cats]):
            cat, _ = Category.objects.get_or_create(
                slug=slugify(cname),
                defaults={"name": cname, "description": cdesc, "display_order": i},
            )
            cat_map[cname] = cat
            for j, (sname, _archs) in enumerate(subcats):
                sub, _ = SubCategory.objects.get_or_create(
                    slug=slugify(f"{cat.slug}-{sname}"),
                    defaults={"name": sname, "category": cat, "display_order": j},
                )
                sub_map[(cname, sname)] = sub

        brand_map = {}
        for b in gen.brands:
            br, _ = Brand.objects.get_or_create(
                slug=slugify(b["name"]),
                defaults={"name": b["name"], "description": b["description"]},
            )
            brand_map[b["name"]] = br

        seller_map = {}
        for sname, sdesc in SELLERS:
            s, _ = Seller.objects.get_or_create(
                slug=slugify(sname),
                defaults={"name": sname, "description": sdesc, "rating": 4.2},
            )
            seller_map[sname] = s
        return cat_map, sub_map, brand_map, seller_map

    # ---------- batch insert ----------
    def _insert_batch(self, items, cat_map, sub_map, brand_map, seller_map):
        products = [
            Product(
                product_id=p["product_id"], sku=p["sku"], name=p["name"], slug=p["slug"],
                brand=brand_map[p["brand"]["name"]],
                category=cat_map[p["category"]],
                subcategory=sub_map[(p["category"], p["subcategory"])],
                seller=seller_map[p["seller"][0]],
                product_type=p["product_type"],
                short_description=p["short_description"][:500],
                detailed_description=p["detailed_description"],
                price=Decimal(str(p["price"])),
                discount_pct=Decimal(str(p["discount_pct"])),
                gst_pct=p["gst_pct"],
                rating=Decimal(str(p["rating"])),
                review_count=p["review_count"],
                availability_status=p["availability"],
                warranty=p["warranty"], return_policy=p["return_policy"],
                weight_kg=Decimal(str(p["weight_kg"])),
                dimensions=p["dimensions"], material=p["material"],
                is_featured=p["is_featured"],
            )
            for p in items
        ]
        Product.objects.bulk_create(products, ignore_conflicts=True)
        # Re-fetch PKs for FK wiring (bulk_create + ignore_conflicts skips ids)
        existing = Product.objects.filter(
            product_id__in=[p["product_id"] for p in items]
        ).in_bulk(field_name="product_id")

        variants, images, specs, reviews = [], [], [], []
        for p in items:
            prod = existing.get(p["product_id"])
            if prod is None:
                continue
            for pos, (sname, sval) in enumerate(p["specifications"].items()):
                specs.append(ProductSpecification(
                    product=prod, name=sname, value=str(sval)[:500], position=pos))
            for i, url in enumerate(p["images"]):
                images.append(ProductImage(
                    product=prod, url=url, alt_text=p["name"][:200], position=i))
            for r in p["reviews"]:
                reviews.append(ProductReview(
                    product=prod, author_name=r["author"], rating=r["rating"],
                    title=r["title"], body=r["body"], is_verified=True))
            for v in p["variants"]:
                variants.append((prod, v))

        variant_objs = [
            ProductVariant(
                variant_id=v["variant_id"], sku=v["sku"], product=prod,
                color=v["color"], size=v["size"], storage=v["storage"],
                price=Decimal(str(v["price"])),
                discount_pct=Decimal(str(v["discount_pct"])),
            )
            for prod, v in variants
        ]
        ProductVariant.objects.bulk_create(variant_objs, ignore_conflicts=True)
        vexisting = ProductVariant.objects.filter(
            variant_id__in=[v["variant_id"] for _, v in variants]
        ).in_bulk(field_name="variant_id")

        inventories, prices, vimages = [], [], []
        for prod, v in variants:
            vo = vexisting.get(v["variant_id"])
            if vo is None:
                continue
            inventories.append(Inventory(variant=vo, quantity=v["stock"]))
            final = round(v["price"] * (1 - v["discount_pct"] / 100), 2)
            prices.append(Price(variant=vo, mrp=Decimal(str(v["price"])),
                               selling_price=Decimal(str(final))))
            for i, url in enumerate(v["images"]):
                vimages.append(ProductImage(
                    variant=vo, url=url,
                    alt_text=f"{prod.name} variant"[:200], position=i))

        Inventory.objects.bulk_create(inventories, ignore_conflicts=True)
        Price.objects.bulk_create(prices)
        ProductImage.objects.bulk_create(images)
        ProductImage.objects.bulk_create(vimages)
        ProductSpecification.objects.bulk_create(specs, ignore_conflicts=True)
        ProductReview.objects.bulk_create(reviews)
        return len(existing)
