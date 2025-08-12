from database import db

class InventoryItem(db.Model):
    __tablename__ = 'inventory_item'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    current_stock = db.Column(db.Integer, nullable=False, default=0)
    unit_price = db.Column(db.Numeric(15, 2), nullable=False, default=0)
    status = db.Column(db.String(20))
    reorder_point = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    @property
    def total_value(self):
        return (self.unit_price or 0) * (self.current_stock or 0)