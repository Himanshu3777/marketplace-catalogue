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
# Create admin superuser from env vars (free plan has no Shell access).
# Set DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL,
# DJANGO_SUPERUSER_PASSWORD in Render Environment.
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  python manage.py createsuperuser --noinput 2>/dev/null || echo "Superuser already exists or creation skipped."
fi
