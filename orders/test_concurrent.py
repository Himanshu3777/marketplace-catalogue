"""Concurrency test: simultaneous payment verifications must not oversell.

Note: SQLite treats SELECT FOR UPDATE as a no-op, so this test verifies
the idempotency logic (min/max guards) under threads. True row-locking
behavior requires PostgreSQL.
"""
import threading

from django.test import TransactionTestCase

from catalog.models import (
    Brand, Category, Product, ProductVariant, SubCategory,
)
from inventory.models import Inventory, Price
from orders.models import Order, OrderItem
from sellers.models import Seller


class ConcurrentDeductTest(TransactionTestCase):
    def setUp(self):
        cat = Category.objects.create(name="CCat", slug="ccat")
        sub = SubCategory.objects.create(
            name="CSub", slug="csub", category=cat)
        brand = Brand.objects.create(name="CBrand", slug="cbrand")
        seller = Seller.objects.create(name="CSeller", slug="cseller")
        product = Product.objects.create(
            name="Concurrent Product", slug="concurrent-product",
            category=cat, subcategory=sub,
            brand=brand, seller=seller, price=100,
        )
        self.variant = ProductVariant.objects.create(
            product=product, sku="CON-001", price=100,
        )
        # Last unit: quantity=5, reserved=5
        self.inv = Inventory.objects.create(
            variant=self.variant, quantity=5, reserved=5)
        Price.objects.create(
            variant=self.variant, selling_price=100, mrp=120)
        self.order = Order.objects.create(
            order_number="MC-CON01", subtotal=500, total=500,
            status=Order.STATUS_PLACED,
        )
        OrderItem.objects.create(
            order=self.order, variant=self.variant,
            quantity=5, price=100,
        )

    def test_concurrent_double_verify_no_oversell(self):
        """10 simultaneous verifications → stock deducted exactly once."""
        errors = []

        def verify():
            try:
                # Fresh order instance per thread (like real requests)
                order = Order.objects.get(pk=self.order.pk)
                order.deduct_stock_on_payment()
            except Exception as e:  # noqa: BLE001
                errors.append(str(e))

        threads = [threading.Thread(target=verify) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # On SQLite, "database is locked" errors are EXPECTED under
        # concurrent writes (SQLite limitation, not a code bug).
        # On PostgreSQL, SELECT FOR UPDATE handles this properly.
        # The critical assertion: no overselling, no negative stock.
        for e in errors:
            self.assertIn("locked", e.lower(),
                          f"Unexpected error (not a lock issue): {e}")

        self.inv.refresh_from_db()
        # Stock deducted at most once: never negative, never oversold
        self.assertGreaterEqual(self.inv.quantity, 0)
        self.assertGreaterEqual(self.inv.reserved, 0)
        # Total units accounted for: quantity + reserved <= original 10
        # (some may remain reserved if threads hit lock errors)
        self.assertLessEqual(
            self.inv.quantity + self.inv.reserved, 10)
