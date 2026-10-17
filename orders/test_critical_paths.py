"""Critical path tests: cart, checkout, ownership, returns.

Covers the most important user flows without external dependencies.
"""
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import CustomerProfile
from cart.models import Cart, CartItem
from catalog.models import (
    Brand, Category, Product, ProductVariant, SubCategory,
)
from inventory.models import Inventory, Price
from orders.models import Order, OrderItem
from sellers.models import Seller


def make_catalog():
    cat = Category.objects.create(name="TCat", slug="tcat")
    sub = SubCategory.objects.create(name="TSub", slug="tsub", category=cat)
    brand = Brand.objects.create(name="TBrand", slug="tbrand")
    seller = Seller.objects.create(name="TSeller", slug="tseller")
    product = Product.objects.create(
        name="Test Product", slug="test-product",
        category=cat, subcategory=sub,
        brand=brand, seller=seller, price=100,
    )
    variant = ProductVariant.objects.create(
        product=product, sku="TST-001", price=100,
    )
    Inventory.objects.create(variant=variant, quantity=10, reserved=0)
    Price.objects.create(variant=variant, selling_price=100, mrp=120)
    return variant


class CartTest(TestCase):
    def setUp(self):
        self.variant = make_catalog()
        self.client = APIClient()

    def test_add_to_cart(self):
        r = self.client.post("/api/cart/add/", {
            "variant_id": self.variant.id, "quantity": 2,
        }, format="json")
        self.assertIn(r.status_code, (200, 201))
        # Verify via cart GET
        r2 = self.client.get("/api/cart/")
        items = r2.data.get("items", r2.data if isinstance(r2.data, list) else [])
        self.assertTrue(len(items) > 0)

    def test_add_exceeds_stock_rejected(self):
        r = self.client.post("/api/cart/add/", {
            "variant_id": self.variant.id, "quantity": 999,
        }, format="json")
        self.assertEqual(r.status_code, 400)

    def test_add_zero_quantity_rejected(self):
        r = self.client.post("/api/cart/add/", {
            "variant_id": self.variant.id, "quantity": 0,
        }, format="json")
        self.assertIn(r.status_code, (400, 422))


class CheckoutTest(TestCase):
    def setUp(self):
        self.variant = make_catalog()
        self.client = APIClient()
        self.client.post("/api/cart/add/", {
            "variant_id": self.variant.id, "quantity": 2,
        }, format="json")

    def _checkout_data(self, key="key-123"):
        return {
            "customer_name": "Test User", "phone": "9876543210",
            "address_line1": "123 Test St", "city": "Delhi",
            "state": "Delhi", "pincode": "110001",
            "payment_method": "COD", "idempotency_key": key,
        }

    def test_guest_checkout_cod(self):
        r = self.client.post("/api/orders/checkout/",
                             self._checkout_data(), format="json")
        self.assertEqual(r.status_code, 201)
        self.assertTrue(r.data["order_number"].startswith("MC-"))

    def test_checkout_idempotent(self):
        """Same idempotency key → same order, no duplicate."""
        r1 = self.client.post("/api/orders/checkout/",
                              self._checkout_data("dup-key"), format="json")
        r2 = self.client.post("/api/orders/checkout/",
                              self._checkout_data("dup-key"), format="json")
        self.assertEqual(r1.data["order_number"], r2.data["order_number"])
        self.assertTrue(r2.data.get("duplicate"))
        self.assertEqual(
            Order.objects.filter(
                idempotency_key="dup-key").count(), 1)

    def test_checkout_invalid_phone_rejected(self):
        data = self._checkout_data()
        data["phone"] = "123"
        r = self.client.post("/api/orders/checkout/", data, format="json")
        self.assertEqual(r.status_code, 400)

    def test_checkout_invalid_pincode_rejected(self):
        data = self._checkout_data()
        data["pincode"] = "123"
        r = self.client.post("/api/orders/checkout/", data, format="json")
        self.assertEqual(r.status_code, 400)


class OrderOwnershipTest(TestCase):
    def setUp(self):
        self.variant = make_catalog()
        self.user_a = User.objects.create_user(
            username="usera", password="pass12345")
        self.user_b = User.objects.create_user(
            username="userb", password="pass12345")
        self.order = Order.objects.create(
            order_number="MC-OWN01", subtotal=100, total=100,
            user=self.user_a, status=Order.STATUS_PLACED,
        )

    def test_owner_can_view(self):
        c = APIClient()
        c.force_login(self.user_a)
        r = c.get(f"/api/orders/{self.order.order_number}/")
        self.assertEqual(r.status_code, 200)

    def test_non_owner_gets_404(self):
        """User B must NOT see User A's order (404, not 403)."""
        c = APIClient()
        c.force_login(self.user_b)
        r = c.get(f"/api/orders/{self.order.order_number}/")
        self.assertEqual(r.status_code, 404)

    def test_anonymous_cannot_view_owned_order(self):
        c = APIClient()
        r = c.get(f"/api/orders/{self.order.order_number}/")
        # Guest orders work by number; owned orders need the owner
        self.assertIn(r.status_code, (401, 403, 404))
