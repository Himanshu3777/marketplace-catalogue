#!/usr/bin/env bash
# Render build script
set -o errexit
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
# Seed demo catalogue on first deploy (free plan has no Shell access).
# Render free tier uses ephemeral storage, so this re-seeds after each deploy.
PRODUCT_COUNT=$(python manage.py shell -c "from catalog.models import Product; print(Product.objects.count())" 2>/dev/null | tail -1 | tr -d '[:space:]')
if [ "$PRODUCT_COUNT" = "0" ]; then
  echo "Seeding catalogue (5000 products)..."
  python manage.py seed_products --products 5000
else
  echo "Catalogue already has $PRODUCT_COUNT products, skipping seed."
fi
