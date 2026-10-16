"""Synthetic catalogue generator.

Produces ORIGINAL product data (fictional brands, generated names/descriptions).
Yields plain dicts; the seed command bulk-inserts them.

Scaling: the generator is a pure iterator — memory stays flat whether you
generate 5,000 or 1,000,000 products. DB writes use bulk_create in batches.
"""
import hashlib
import itertools
import random
from decimal import Decimal

from . import pools
from . import pools2  # noqa: F401  (extends CATEGORIES)
from . import pools3  # noqa: F401  (extends CATEGORIES)

SELLERS = [
    ("RetailKart", "Multi-category retail seller."),
    ("ValueDeals", "Discount-focused marketplace seller."),
    ("PrimeGoods", "Premium products seller."),
    ("DailyNeeds Co", "Grocery and essentials seller."),
    ("TechHub", "Electronics specialist seller."),
    ("FashionNest", "Apparel and lifestyle seller."),
    ("HomeEssentials", "Home and furniture seller."),
    ("SportZone", "Sports and fitness seller."),
]

REVIEW_TITLES = [
    "Great value for money", "Exceeded expectations", "Good quality",
    "Decent product", "Highly recommended", "Value pick", "Solid build",
]
REVIEW_BODIES = [
    "Does exactly what it promises. Packaging was good and delivery was quick.",
    "Quality is solid for the price. Would buy again.",
    "Works well so far. Matches the description on the site.",
    "Good product overall, minor packaging scuffs but item is fine.",
    "Impressive finish and performance. Recommended for first-time buyers.",
]
REVIEWERS = ["Aarav", "Priya", "Rohan", "Sneha", "Vikram", "Ananya", "Karan", "Divya",
             "Arjun", "Meera", "Aditya", "Kavya", "Nikhil", "Pooja", "Rahul", "Ishita"]


def _slug(text):
    return "".join(c.lower() if c.isalnum() else "-" for c in text).strip("-").replace("--", "-")


def _stable_int(*parts):
    h = hashlib.md5("|".join(map(str, parts)).encode()).hexdigest()
    return int(h[:8], 16)


class CatalogueGenerator:
    def __init__(self, seed=42):
        self.rng = random.Random(seed)
        self.used_skus = set()
        self.used_names = set()
        self.model_counters = {}
        self.brands = pools.build_brands()
        self._brand_idx = 0

    # ---------- helpers ----------
    def _next_brand(self):
        b = self.brands[self._brand_idx % len(self.brands)]
        self._brand_idx += 1
        return b

    def _unique_sku(self, *parts):
        n = _stable_int(*parts) % 900000 + 100000
        sku = f"SKU-{parts[0]}-{n}"
        i = 1
        while sku in self.used_skus:
            i += 1
            sku = f"SKU-{parts[0]}-{n}-{i}"
        self.used_skus.add(sku)
        return sku

    def _model_no(self, brand, line):
        key = (brand, line)
        self.model_counters[key] = self.model_counters.get(key, 0) + 1
        return f"{self.model_counters[key]:03d}"

    def _desc(self, brand, ptype, specs):
        spec_txt = ", ".join(f"{k} {v}" for k, v in list(specs.items())[:3])
        return (
            f"The {brand} {ptype} is designed for everyday reliability. "
            f"Key highlights include {spec_txt}. Built with quality materials and "
            f"backed by manufacturer support, it is a dependable choice in its class."
        )

    # ---------- main ----------
    def iter_products(self, target_count):
        """Yield product dicts until target_count unique products are produced."""
        # Flatten archetypes with weights
        flat = []
        for cat_i, (cat_name, cat_desc, subcats) in enumerate(pools.CATEGORIES):
            for sub_i, (sub_name, archetypes) in enumerate(subcats):
                for arch_i, arch in enumerate(archetypes):
                    flat.append((cat_i, sub_name, cat_name, cat_desc, sub_i, arch_i, arch))
        # Round-robin distribution for even coverage
        produced = 0
        round_n = 0
        while produced < target_count:
            made_this_round = 0
            for entry in flat:
                if produced >= target_count:
                    break
                p = self._make_product(*entry, round_n)
                if p is None:
                    continue
                made_this_round += 1
                produced += 1
                yield p
            round_n += 1
            if made_this_round == 0:
                break  # exhausted unique space

    def _make_product(self, cat_i, sub_name, cat_name, cat_desc, sub_i, arch_i, arch, round_n):
        (ptype, model_lines, price_range, spec_names,
         variant_axes, weight_range, warranty) = arch
        rng = self.rng
        brand = self._next_brand()
        line = rng.choice(model_lines)
        model_no = self._model_no(brand["name"], line)
        gen = rng.choice(["", " Pro", " Max", " Lite", " Plus", " Neo"])
        name = f"{brand['name']} {line} {model_no}{gen} {ptype}"
        if name in self.used_names:
            return None
        self.used_names.add(name)

        lo, hi = price_range
        # log-uniform-ish price within range
        price = round(rng.uniform(lo, hi), 2)
        discount = round(rng.choice([0, 0, 5, 10, 15, 20, 25, 30]), 2)
        rating = round(rng.uniform(3.2, 4.9), 2)
        review_count = rng.choice([0, 3, 12, 45, 120, 340, 890, 2100])
        stock_total = rng.choice([0, 5, 25, 80, 200, 500])

        specs = {}
        for sname in spec_names:
            vals = pools.SPEC_VALUES.get(sname)
            specs[sname] = rng.choice(vals) if vals else f"{rng.randint(1, 99)} units"

        # Variants: cartesian of axes, capped at 6
        axes = [(k, v) for k, v in variant_axes.items()]
        combos = list(itertools.product(*[v for _, v in axes]))[:6] if axes else [()]
        variants = []
        for ci, combo in enumerate(combos):
            vaxes = dict(zip([k for k, _ in axes], combo)) if axes else {}
            vprice = round(price * rng.uniform(0.92, 1.12), 2)
            vsku = self._unique_sku("V", brand["name"][:3].upper(), model_no, ci)
            vqty = max(0, stock_total // max(1, len(combos)) + rng.randint(-5, 10))
            variants.append({
                "variant_id": f"VAR-{_stable_int(name, ci) % 900000 + 100000}",
                "sku": vsku,
                "color": vaxes.get("color"),
                "size": vaxes.get("size"),
                "storage": vaxes.get("storage"),
                "price": vprice,
                "discount_pct": discount,
                "stock": vqty,
                "images": [
                    f"https://picsum.photos/seed/{vsku}-{i}/600/600"
                    for i in range(2)
                ],
            })

        images = [f"https://picsum.photos/seed/{_slug(name)[:40]}-{i}/600/600" for i in range(3)]
        n_reviews = min(review_count, 5)
        reviews = []
        for _ in range(n_reviews):
            reviews.append({
                "author": rng.choice(REVIEWERS),
                "rating": rng.choice([3, 4, 4, 5, 5]),
                "title": rng.choice(REVIEW_TITLES),
                "body": rng.choice(REVIEW_BODIES),
            })

        pid = f"PRD-{_stable_int(name) % 90000000 + 10000000}"
        return {
            "product_id": pid,
            "sku": self._unique_sku("P", pid),
            "name": name,
            "slug": f"{_slug(name)}-{pid.lower()}",
            "brand": brand,
            "category": cat_name,
            "category_desc": cat_desc,
            "subcategory": sub_name,
            "product_type": ptype,
            "short_description": f"{brand['name']} {line} {ptype} — {specs.get(spec_names[0], '')}.".strip()[:500],
            "detailed_description": self._desc(brand["name"], ptype, specs),
            "specifications": specs,
            "price": price,
            "discount_pct": discount,
            "gst_pct": Decimal("18.00"),
            "rating": rating,
            "review_count": review_count,
            "availability": ("out_of_stock" if stock_total == 0
                             else "low_stock" if stock_total < 15 else "in_stock"),
            "warranty": warranty,
            "return_policy": "7-day easy replacement; 10-day refund on defects.",
            "weight_kg": round(rng.uniform(*weight_range), 3),
            "dimensions": f"{rng.randint(10,80)}x{rng.randint(10,60)}x{rng.randint(5,40)} cm",
            "material": None,  # NULL where not universally applicable
            "seller": rng.choice(SELLERS),
            "images": images,
            "variants": variants,
            "reviews": reviews,
            "is_featured": rng.random() < 0.05,
        }
