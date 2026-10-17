"""Verification tests for stock locking fix (orders/models.py).

Tests deduct_stock_on_payment and restock_on_cancel_after_payment
for correctness and idempotency.
"""
from django.test import TestCase

from catalog.models import (
    Brand, Category, Product, ProductVariant, SubCategory,
)
from inventory.models import Inventory
from orders.models import Order, OrderItem
from sellers.models import Seller


class StockLockingTest(TestCase):
    def setUp(self):
        cat = Category.objects.create(name="TestCat", slug="testcat")
        sub = SubCategory.objects.create(
            name="TestSub", slug="testsub", category=cat)
        brand = Brand.objects.create(name="TestBrand", slug="testbrand")
        seller = Seller.objects.create(name="TestSeller", slug="testseller")
        product = Product.objects.create(
            name="Test Product", slug="test-product",
            category=cat, subcategory=sub,
            brand=brand, seller=seller, price=100,
        )
        self.variant = ProductVariant.objects.create(
            product=product, sku="TEST-001", price=100,
        )
        self.inv = Inventory.objects.create(
            variant=self.variant, quantity=10, reserved=5,
        )
        self.order = Order.objects.create(
            order_number="MC-TEST01", subtotal=500, total=500,
            status=Order.STATUS_PLACED,
        )
        OrderItem.objects.create(
            order=self.order, variant=self.variant,
            quantity=5, price=100,
        )

    def test_deduct_stock_on_payment(self):
        """Payment deducts exactly the reserved quantity."""
        self.order.deduct_stock_on_payment()
        self.inv.refresh_from_db()
        self.assertEqual(self.inv.quantity, 5)   # 10 - 5
        self.assertEqual(self.inv.reserved, 0)    # 5 - 5

    def test_deduct_is_idempotent(self):
        """Second call must NOT deduct again."""
        self.order.deduct_stock_on_payment()
        self.order.deduct_stock_on_payment()
        self.inv.refresh_from_db()
        self.assertEqual(self.inv.quantity, 5)
        self.assertEqual(self.inv.reserved, 0)

    def test_restock_on_cancel(self):
        """Cancel after payment returns stock."""
        self.order.deduct_stock_on_payment()
        self.order.restock_on_cancel_after_payment()
        self.inv.refresh_from_db()
        self.assertEqual(self.inv.quantity, 10)  # back to original

    def test_stock_never_negative(self):
        """Deduction clamps at zero even if reserved > quantity."""
        self.inv.reserved = 20
        self.inv.quantity = 3
        self.inv.save()
        self.order.deduct_stock_on_payment()
        self.inv.refresh_from_db()
        self.assertGreaterEqual(self.inv.quantity, 0)
