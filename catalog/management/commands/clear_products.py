"""Delete generated catalogue data (with safety confirmation).

Usage:
    python manage.py clear_products
    python manage.py clear_products --force
"""
from django.core.management.base import BaseCommand

from catalog.models import Product


class Command(BaseCommand):
    help = "Delete all products and their related generated data."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true",
                            help="skip confirmation prompt")

    def handle(self, *args, **opts):
        count = Product.objects.count()
        if count == 0:
            self.stdout.write("No products to delete.")
            return
        if not opts["force"]:
            answer = input(
                f"Delete {count} products (+ variants, images, inventory, "
                f"prices, reviews)? This cannot be undone. [y/N] "
            ).strip().lower()
            if answer != "y":
                self.stdout.write("Aborted.")
                return
        # Cascades handle variants/images/specs/inventory/prices/reviews.
        deleted, _ = Product.objects.all().delete()
        self.stdout.write(
            self.style.SUCCESS(f"Deleted {deleted} objects (products + related)."))
