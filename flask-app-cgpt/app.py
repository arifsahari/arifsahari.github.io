import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pandas as pd
from models import db, UploadedRecord  # Import the db and model from models.py
from sqlalchemy.exc import SQLAlchemyError

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure your MySQL connection using an environment variable DATABASE_URL.
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "mysql+pymysql://mysql:root@localhost:3306/order_checking")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the SQLAlchemy instance with the Flask app.
db.init_app(app)

# Example route to upload file and insert records into the database.
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
        db.session.rollback()
        return jsonify(error=str(e)), 500

# Other routes go here...
# For example, routes for searching parent records and verifying child record checks.

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables if they don't exist.
    app.run(debug=True)
