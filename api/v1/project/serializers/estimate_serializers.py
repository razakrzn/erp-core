from rest_framework import serializers

from apps.Projects.models import Labour, Material, Other, Project
from apps.assessment.models import QuoteItem
from apps.hrm.models.designation import Designation
from apps.inventory.models import Product


class EstimateProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["id", "job_number", "project_name", "status"]


class EstimateQuoteItemSerializer(serializers.ModelSerializer):
    quote_number = serializers.CharField(source="quote.quote_number", read_only=True)
    boq_item_name = serializers.CharField(source="boq_item.name", read_only=True)

    class Meta:
        model = QuoteItem
        fields = [
            "id",
            "name",
            "quote",
            "quote_number",
            "boq_item",
            "boq_item_name",
            "category",
            "quantity",
        ]


class EstimateProductSerializer(serializers.ModelSerializer):
    unit_name = serializers.CharField(source="unit.name", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "sku",
            "product_code",
            "stock_on_hand",
            "unit",
            "unit_name",
        ]


class EstimateDesignationSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.name", read_only=True)

    class Meta:
        model = Designation
        fields = ["id", "name", "department", "department_name", "is_active"]


class EstimateMaterialWriteSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    item = serializers.PrimaryKeyRelatedField(queryset=QuoteItem.objects.all(), allow_null=True, required=False)
    material = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), allow_null=True, required=False)

    class Meta:
        model = Material
        fields = ["id", "project", "item", "material", "req_qty", "notes_remarks"]


class EstimateMaterialListSerializer(serializers.ModelSerializer):
    project_detail = EstimateProjectSerializer(source="project", read_only=True)
    item_detail = EstimateQuoteItemSerializer(source="item", read_only=True)
    material_detail = EstimateProductSerializer(source="material", read_only=True)
    stock_on_hand = serializers.SerializerMethodField()
    unit_name = serializers.SerializerMethodField()

    class Meta:
        model = Material
        fields = [
            "id",
            "project",
            "project_detail",
            "item",
            "item_detail",
            "material",
            "material_detail",
            "req_qty",
            "stock_on_hand",
            "unit_name",
        ]

    def get_stock_on_hand(self, obj):
        return str(obj.stock_on_hand)

    def get_unit_name(self, obj):
        return obj.unit.name if obj.unit else None


class EstimateMaterialDetailSerializer(EstimateMaterialListSerializer):
    class Meta(EstimateMaterialListSerializer.Meta):
        fields = EstimateMaterialListSerializer.Meta.fields + ["notes_remarks"]


class EstimateLabourWriteSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    designation = serializers.PrimaryKeyRelatedField(
        queryset=Designation.objects.all(),
        allow_null=True,
        required=False,
    )

    class Meta:
        model = Labour
        fields = ["id", "project", "designation", "hrs", "rate", "amount"]
        read_only_fields = ["amount"]


class EstimateLabourListSerializer(serializers.ModelSerializer):
    project_detail = EstimateProjectSerializer(source="project", read_only=True)
    designation_detail = EstimateDesignationSerializer(source="designation", read_only=True)

    class Meta:
        model = Labour
        fields = [
            "id",
            "project",
            "project_detail",
            "designation",
            "designation_detail",
            "hrs",
            "rate",
            "amount",
        ]


class EstimateLabourDetailSerializer(EstimateLabourListSerializer):
    pass


class EstimateOtherWriteSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())

    class Meta:
        model = Other
        fields = ["id", "project", "item_description", "amount"]


class EstimateOtherListSerializer(serializers.ModelSerializer):
    project_detail = EstimateProjectSerializer(source="project", read_only=True)

    class Meta:
        model = Other
        fields = [
            "id",
            "project",
            "project_detail",
            "item_description",
            "amount",
        ]


class EstimateOtherDetailSerializer(EstimateOtherListSerializer):
    pass
