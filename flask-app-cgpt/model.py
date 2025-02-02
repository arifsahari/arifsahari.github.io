# 1. Define a Model for Uploaded Records
# models.py (or in your app.py if you keep it simple)
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class UploadedRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tracking_number = db.Column(db.String(100), nullable=False)
    sku_reference = db.Column(db.String(100), nullable=False)
    product_name = db.Column(db.String(200))
    quantity = db.Column(db.Integer, nullable=False)
    # You can add additional fields as needed

    def __repr__(self):
        return f"<UploadedRecord {self.sku_reference} qty={self.quantity}>"


# 2. Endpoint to Handle File Uploadv
import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pandas as pd
from models import db, UploadedRecord  # assuming models.py is imported properly

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure your MySQL connection using an environment variable (set DATABASE_URL on Render)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "mysql+pymysql://username:password@localhost:3306/yourdbname")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/upload_file', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    if not file:
        return jsonify(error="No file uploaded"), 400

    filename = file.filename
    if not (filename.endswith('.csv') or filename.endswith('.xlsx')):
        return jsonify(error="Unsupported file format"), 400

    try:
        # Load file data
        df = pd.read_csv(file) if filename.endswith('.csv') else pd.read_excel(file)

        # Rename columns as expected
        mapping = {
            'Items Barcode': 'SKU Reference No.',
            'AWB Number': 'Tracking Number*',
            'Item Name': 'Product Name',
            'Item Quantity': 'Quantity'
        }
        df.rename(columns=mapping, inplace=True)

        # Validate required columns exist
        for col in mapping.values():
            if col not in df.columns:
                return jsonify(error=f"Missing column {col} in uploaded file."), 400

        inserted_count = 0
        duplicates = []
        for index, row in df.iterrows():
            # Check duplicate: assume uniqueness based on tracking_number and sku_reference
            existing = UploadedRecord.query.filter_by(
                tracking_number=row['Tracking Number*'],
                sku_reference=row['SKU Reference No.']
            ).first()
            if existing:
                duplicates.append(row['Tracking Number*'])
                continue
            record = UploadedRecord(
                tracking_number=row['Tracking Number*'],
                sku_reference=row['SKU Reference No.'],
                product_name=row['Product Name'],
                quantity=int(row['Quantity'])
            )
            db.session.add(record)
            inserted_count += 1

        db.session.commit()
        message = f"Successfully uploaded {inserted_count} records."
        if duplicates:
            message += f" Duplicates skipped: {', '.join(duplicates)}."
        return jsonify(message=message), 200
    except Exception as e:
        return jsonify(error=str(e)), 500


# 3. Endpoints for Parent and Child Record Checks

# Search Parent Records
@app.route('/search_parent', methods=['POST'])
def search_parent():
    data_req = request.get_json()
    query = data_req.get('query', '')
    # For example, search by product name (you can adjust as needed)
    results = UploadedRecord.query.filter(UploadedRecord.product_name.ilike(f"%{query}%")).all()
    records = [{
        "id": r.id,
        "tracking_number": r.tracking_number,
        "sku_reference": r.sku_reference,
        "product_name": r.product_name,
        "quantity": r.quantity
    } for r in results]
    return jsonify(records=records)

# Check Child Records (Quantity Verification)
@app.route('/check_child', methods=['POST'])
def check_child():
    data_req = request.get_json()
    record_id = data_req.get('record_id')
    scanned_qty = int(data_req.get('scanned_qty', 0))
    record = UploadedRecord.query.get(record_id)
    if not record:
        return jsonify(error="Record not found"), 404
    expected_qty = record.quantity
    if scanned_qty == expected_qty:
        return jsonify(message="Quantity correct"), 200
    else:
        return jsonify(message=f"Quantity mismatch: expected {expected_qty}, got {scanned_qty}"), 200
