# inventory/models/brand.py


from .base import BaseMasterModel


class Brand(BaseMasterModel):

    class Meta(BaseMasterModel.Meta):
        db_table = "inv_brands"

    def __str__(self):
        return self.name
