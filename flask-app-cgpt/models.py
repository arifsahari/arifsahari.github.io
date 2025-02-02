# 1. Define a Model for Uploaded Records
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class UploadedRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tracking_number = db.Column(db.String(100), nullable=False)
    sku_reference = db.Column(db.String(100), nullable=False)
    product_name = db.Column(db.String(200))
    quantity = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<UploadedRecord {self.sku_reference} qty={self.quantity}>"
