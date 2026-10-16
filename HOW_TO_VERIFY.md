# Where things run — read this first!

## The server runs on YOUR computer, not on the internet

When you run `python manage.py runserver`, Django starts on YOUR machine at:
- http://127.0.0.1:8000/  (storefront)
- http://127.0.0.1:8000/api/products/  (API)

`127.0.0.1` means "this computer". Nobody else can open it — it's only for
you to develop and test.

## How to verify everything works

### 1. API checks (in your browser)
| What | URL |
|---|---|
| Product list | http://127.0.0.1:8000/api/products/ |
| Filtered | http://127.0.0.1:8000/api/products/?category=electronics&min_price=10000&ordering=price |
| Search | http://127.0.0.1:8000/api/products/?search=laptop |
| Categories | http://127.0.0.1:8000/api/categories/ |
| One product (copy a slug from the list) | http://127.0.0.1:8000/api/products/<slug>/ |
| Its variants | http://127.0.0.1:8000/api/products/<slug>/variants/ |
| Its reviews | http://127.0.0.1:8000/api/products/<slug>/reviews/ |

You should see JSON with `count`, `results`, product names, prices, etc.

### 2. Storefront checks (in your browser)
- http://127.0.0.1:8000/ — product grid, filter sidebar, sorting, pagination
- Click any product — detail page with variant selector, specs, reviews
- Use the search box at the top

### 3. Database checks (in terminal)
```bash
python manage.py shell
```
```python
from catalog.models import Product
Product.objects.count()          # how many products
Product.objects.first().name     # a sample name
```

### 4. Management commands (in terminal, project folder)
```bash
python manage.py seed_products --products 5000   # add more data
python manage.py clear_products                  # delete with confirmation
```

## Commands run in YOUR terminal, in the project folder
`cd` into the extracted folder first, then run the commands there.
