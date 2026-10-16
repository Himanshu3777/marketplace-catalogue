# MarketPlace — API-first E-commerce Catalogue

Original/synthetic product catalogue for development & testing.
**No real marketplace data is copied.** All brands, names, descriptions and
images are fictional/generated and designed to be replaceable with licensed
data later without schema changes.

## Quick start

```bash
pip install django djangorestframework django-filter
python manage.py migrate
python manage.py seed_products --products 5000   # or 50000 / 100000
python manage.py runserver
```

- Storefront: http://127.0.0.1:8000/
- API root: http://127.0.0.1:8000/api/products/

```bash
python manage.py clear_products        # with confirmation
python manage.py clear_products --force
```

## 1. Database architecture

Normalized relational design (SQLite dev / Postgres prod-ready):

```
Category 1───* SubCategory 1───* Product *───1 Brand
                                        *───1 Seller
              Product 1───* ProductVariant 1───1 Inventory
                                           1───* Price (history)
              Product 1───* ProductImage / ProductSpecification / ProductReview
```

No duplication: category/brand/seller live once; products reference them by FK.
Images, specs, variants are child rows. Prices keep history via `valid_from/to`.

## 2. Models & relationships

| App | Models |
|---|---|
| `catalog` | Category, SubCategory, Brand, Product, ProductVariant, ProductImage, ProductSpecification |
| `sellers` | Seller |
| `inventory` | Inventory (per variant), Price (per variant, historized) |
| `reviews` | ProductReview |

Key constraints: unique `product_id`/`sku`/`variant_id`, unique variant axes per
product, `price >= 0`, `discount 0–90%`, `selling_price <= mrp`, rating 1–5,
image must belong to a product or variant. NULL (not fake values) for
non-applicable attributes (e.g. `storage` on a t-shirt).

## 3. Category hierarchy

30 categories → 108 subcategories → products → variants, e.g.:

```
Electronics → Smartphones → "AeroCore Cirrus 001 5G Smartphone"
    ├── 128GB / Black     ├── 128GB / Blue
    ├── 256GB / Black     └── 256GB / Blue
```

## 4. API architecture

Django REST Framework, JSON only, no HTML in CRUD:

```
GET    /api/categories/  /api/categories/<slug>/
GET    /api/subcategories/?category=<slug>
GET    /api/brands/
GET    /api/products/  (+ filters below)
GET    /api/products/<slug>/
POST   /api/products/   PUT /api/products/<slug>/
PATCH  /api/products/<slug>/  DELETE /api/products/<slug>/
GET    /api/products/<slug>/variants/
GET    /api/products/<slug>/reviews/
```

Filters: `?category=electronics&subcategory=smartphones&brand=x&seller=y`
`?min_price=1000&max_price=50000` `?min_rating=4` `?min_discount=10`
`?availability=in_stock` `?in_stock=true` `?product_type=` `?color=` `?size=`
`?is_featured=true` `?search=laptop` `?ordering=price` / `-rating`
`?page=1&page_size=20`

## 5. Data-generation strategy

`catalog/data/` holds pools (30 categories, 108 subcategories, 520 fictional
brands from syllable combinators, spec value pools). `generator.py` is a pure
iterator yielding product dicts — brand + model line + incrementing model
number + generation suffix guarantees unique names; SKUs derive from stable
hashes. `seed_products` bulk-inserts in batches (default 1000):

```
python manage.py seed_products --products 5000
python manage.py seed_products --products 50000 --batch 2000
```

## 6. Duplicate prevention

- DB: unique constraints on product_id, sku, variant_id, (product,color,size,storage), (product,spec name)
- App: in-memory `used_skus`/`used_names` sets during generation; `ignore_conflicts=True` on bulk_create
- Validation: `CheckConstraint`s on prices/discounts/ratings; FK validation on category/subcategory/brand

## 7. Scaling 5,000 → 1,000,000+

- **Memory-flat generator**: iterator + `bulk_create` batches; never loads the catalogue into memory
- **Indexes** on every filter/sort column (category, brand, price, rating, availability, color, size, slugs)
- **QuerySets**: `select_related` + `prefetch_related` + annotations; lightweight list serializer vs. detail serializer
- **Pagination** on every list endpoint (max 100/page)
- **Path to 1M**: same schema; switch SQLite→Postgres, raise `--batch`, run seed per category shard; add DB read replica + HTTP caching for listings

## Frontend

Vanilla JS (`fetch()`), no business logic in HTML:

- `/` — listing + filter sidebar + sorting + pagination
- `/product/<slug>/` — detail + variant selector + specs + reviews
- `/category/<slug>/` — category + subcategories
- `/search/?q=` — search results

## Seeded volume (default run)

30 categories · 108 subcategories · 520 brands · 8 sellers ·
~5,000 products · ~18,000 variants · ~15,000 images · ~25,000 reviews
