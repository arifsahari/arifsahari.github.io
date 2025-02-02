import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import pandas as pd

# Initialize the Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# --- Database (MySQL) Setup with SQLAlchemy ---
# Configure your MySQL connection using an environment variable DATABASE_URL.
# Example DATABASE_URL: "mysql+pymysql://username:password@host:port/dbname"
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "mysql+pymysql://username:password@localhost:3306/yourdbname")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define a simple model to record scanned items
class ScannedItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    awb_number = db.Column(db.String(100), nullable=False)
    sku_reference = db.Column(db.String(100), nullable=False)
    count = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"<ScannedItem {self.sku_reference} count={self.count}>"

# --- Google Sheets Integration Setup ---
# To use Google Sheets as your "database", you can use gspread.
# Install gspread and oauth2client: pip install gspread oauth2client
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def init_gsheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name("path/to/your/credentials.json", scope)
    client = gspread.authorize(creds)
    # Open the first sheet of your Google Sheet (make sure to share your sheet with your service account email)
    sheet = client.open("Your Google Sheet Name").sheet1
    return sheet

def update_gsheet(awb_number, scanned_items):
    """Append each scanned item as a new row in Google Sheets."""
    sheet = init_gsheet()
    for sku, count in scanned_items.items():
        sheet.append_row([awb_number, sku, count])

# --- In-Memory Data Loading (from CSV/Excel) ---
data = pd.DataFrame()

def load_data(file_path):
    global data
    # Load CSV or Excel file based on file extension
    data = pd.read_csv(file_path) if file_path.endswith('.csv') else pd.read_excel(file_path)
    # Rename columns as per your mapping
    data.rename(columns={
        'Items Barcode': 'SKU Reference No.',
        'AWB Number': 'Tracking Number*',
        'Item Name': 'Product Name',
        'Item Quantity': 'Quantity'
    }, inplace=True)

# --- Helper: Save scanned item info into MySQL ---
def save_scanned_item(awb_number, item_barcode, count):
    scanned = ScannedItem.query.filter_by(awb_number=awb_number, sku_reference=item_barcode).first()
    if scanned:
        scanned.count = count
    else:
        scanned = ScannedItem(awb_number=awb_number, sku_reference=item_barcode, count=count)
        db.session.add(scanned)
    db.session.commit()

# --- Routes ---
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        awb_input = request.form.get('awb_number')
        if awb_input in data['Tracking Number*'].values:
            session['awb_number'] = awb_input
            # Initialize a dictionary to track scanned items
            session['scanned_items'] = {}
            return redirect(url_for('scan_items'))
        else:
            return render_template('index.html', error="AWB not found. Try again.")
    return render_template('index.html')

@app.route('/scan_items', methods=['GET', 'POST'])
def scan_items():
    awb_number = session.get('awb_number', None)
    if not awb_number:
        return redirect(url_for('index'))

    # Filter items for the given AWB
    items = data[data['Tracking Number*'] == awb_number]

    if request.method == 'POST':
        item_input = request.form.get('item_barcode')
        if item_input in items['SKU Reference No.'].values:
            # Update session dictionary with scanned item count
            scanned = session.get('scanned_items', {})
            scanned[item_input] = scanned.get(item_input, 0) + 1
            session['scanned_items'] = scanned

            # Save/update scanned item info in MySQL
            save_scanned_item(awb_number, item_input, scanned[item_input])

            # Optionally, update your Google Sheet here
            # (For example, you might call update_gsheet(awb_number, scanned) periodically or after each scan)
            # update_gsheet(awb_number, scanned)

            # Check if scanned count meets or exceeds required quantity
            required_qty = int(items[items['SKU Reference No.'] == item_input]['Quantity'].values[0])
            if scanned[item_input] >= required_qty:
                # Remove the item from the list if fully scanned
                items = items[items['SKU Reference No.'] != item_input]
            if items.empty:
                session.clear()
                return redirect(url_for('index'))
            return redirect(url_for('scan_items'))
        else:
            return render_template('scan_items.html', awb_number=awb_number, items=items, error="Invalid Item. Try again.")
    return render_template('scan_items.html', awb_number=awb_number, items=items)

if __name__ == '__main__':
    # On first run, uncomment the next lines to create your MySQL tables:
    # with app.app_context():
    #     db.create_all()
    app.run(debug=True)
