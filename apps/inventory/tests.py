from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from api.v1.inventory.serializers import GoodsReceiptSerializer

from .models import GoodsReceipt, GoodsReceiptItem, Product, PurchaseOrder, PurchaseOrderLineItem


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


class GoodsReceiptApprovalTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="approver",
            email="approver@example.com",
            password="password",
        )
        self.purchase_order = PurchaseOrder.objects.create(
            payment_terms="Net 30",
            shipping_delivery_terms="Delivery",
            po_issued_date="2026-06-06",
            created_by=self.user,
            is_approved=True,
        )
        self.po_line_item = PurchaseOrderLineItem.objects.create(
            purchase_order=self.purchase_order,
            product_code="SHEET-001",
            description="Sheet",
            unit="Nos",
            requested_qty=Decimal("10.00"),
            negotiated_price=Decimal("5.00"),
        )

    def _valid_payload(self, **overrides):
        payload = {
            "purchase_order_id": self.purchase_order.id,
            "grn_recording_date": "2026-06-06",
            "overall_quality_status": "accepted",
            "quality_notes": "",
            "material_intakes": [
                {
                    "purchase_order_line_item": self.po_line_item.id,
                    "qty_good": "2.00",
                    "qty_rejected": "0.00",
                    "rejection_reason": "",
                }
            ],
        }
        payload.update(overrides)
        return payload

    def test_goods_receipt_create_is_approved_by_default(self):
        serializer = GoodsReceiptSerializer(data=self._valid_payload(is_approved=False, is_rejected=True))
        self.assertTrue(serializer.is_valid(), serializer.errors)

        goods_receipt = serializer.save()

        self.assertTrue(goods_receipt.is_approved)
        self.assertFalse(goods_receipt.is_rejected)
        self.assertEqual(goods_receipt.reject_note, "")
        self.assertEqual(goods_receipt.status, "Approved")

    def test_goods_receipt_update_resets_to_pending(self):
        goods_receipt = GoodsReceipt.objects.create(
            purchase_order=self.purchase_order,
            is_approved=True,
            is_rejected=False,
        )
        GoodsReceiptItem.objects.create(
            goods_receipt=goods_receipt,
            purchase_order_line_item=self.po_line_item,
            qty_good=Decimal("2.00"),
            qty_rejected=Decimal("0.00"),
        )

        serializer = GoodsReceiptSerializer(goods_receipt, data=self._valid_payload(quality_notes="Edited"), partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        goods_receipt = serializer.save()

        self.assertFalse(goods_receipt.is_approved)
        self.assertFalse(goods_receipt.is_rejected)
        self.assertEqual(goods_receipt.reject_note, "")
        self.assertEqual(goods_receipt.status, "Pending")

    def test_goods_receipt_status_tracks_rejected_flag(self):
        goods_receipt = GoodsReceipt.objects.create(
            purchase_order=self.purchase_order,
            is_approved=False,
            is_rejected=True,
            reject_note="Quantity mismatch",
        )

        self.assertEqual(goods_receipt.status, "Rejected")
