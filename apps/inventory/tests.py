from decimal import Decimal

from django.test import TestCase

from .models import Product


class ProductStockTests(TestCase):
    def test_available_is_stock_on_hand_less_reserved(self):
        product = Product.objects.create(
            name="Sheet",
            opening_stock=10,
            purchased_stock=Decimal("5.00"),
            reserved=Decimal("4.00"),
        )

        self.assertEqual(product.stock_on_hand, Decimal("15.00"))
        self.assertEqual(product.available, Decimal("11.00"))

    def test_available_can_be_negative_to_show_over_allocation(self):
        product = Product.objects.create(
            name="Over-allocated sheet",
            opening_stock=2,
            reserved=Decimal("3.00"),
        )

        self.assertEqual(product.available, Decimal("-1.00"))

    def test_partial_save_persists_recalculated_available(self):
        product = Product.objects.create(name="Reserved sheet", opening_stock=10)

        product.reserved = Decimal("6.00")
        product.save(update_fields=["reserved"])
        product.refresh_from_db()

        self.assertEqual(product.stock_on_hand, Decimal("10.00"))
        self.assertEqual(product.available, Decimal("4.00"))
