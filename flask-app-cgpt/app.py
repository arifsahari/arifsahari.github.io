from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your_secret_key'

data = pd.DataFrame()

def load_data(file_path):
    global data
    data = pd.read_csv(file_path) if file_path.endswith('.csv') else pd.read_excel(file_path)
    data.rename(columns={
        'Items Barcode': 'SKU Reference No.',
        'AWB Number': 'Tracking Number*',
        'Item Name': 'Product Name',
        'Item Quantity': 'Quantity'
    }, inplace=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        awb_input = request.form.get('awb_number')
        if awb_input in data['Tracking Number*'].values:
            session['awb_number'] = awb_input
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

    items = data[data['Tracking Number*'] == awb_number]
    if request.method == 'POST':
        item_input = request.form.get('item_barcode')
        if item_input in items['SKU Reference No.'].values:
            session['scanned_items'][item_input] = session['scanned_items'].get(item_input, 0) + 1
            if session['scanned_items'][item_input] >= int(items[items['SKU Reference No.'] == item_input]['Quantity'].values[0]):
                items = items[items['SKU Reference No.'] != item_input]
            if items.empty:
                session.clear()
                return redirect(url_for('index'))
            return redirect(url_for('scan_items'))
        else:
            return render_template('scan_items.html', awb_number=awb_number, items=items, error="Invalid Item. Try again.")
    return render_template('scan_items.html', awb_number=awb_number, items=items)

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your_secret_key'

data = pd.DataFrame()

def load_data(file_path):
    global data
    data = pd.read_csv(file_path) if file_path.endswith('.csv') else pd.read_excel(file_path)
    data.rename(columns={
        'Items Barcode': 'SKU Reference No.',
        'AWB Number': 'Tracking Number*',
        'Item Name': 'Product Name',
        'Item Quantity': 'Quantity'
    }, inplace=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        awb_input = request.form.get('awb_number')
        if awb_input in data['Tracking Number*'].values:
            session['awb_number'] = awb_input
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

    items = data[data['Tracking Number*'] == awb_number]
    if request.method == 'POST':
        item_input = request.form.get('item_barcode')
        if item_input in items['SKU Reference No.'].values:
            session['scanned_items'][item_input] = session['scanned_items'].get(item_input, 0) + 1
            if session['scanned_items'][item_input] >= int(items[items['SKU Reference No.'] == item_input]['Quantity'].values[0]):
                items = items[items['SKU Reference No.'] != item_input]
            if items.empty:
                session.clear()
                return redirect(url_for('index'))
            return redirect(url_for('scan_items'))
        else:
            return render_template('scan_items.html', awb_number=awb_number, items=items, error="Invalid Item. Try again.")
    return render_template('scan_items.html', awb_number=awb_number, items=items)

if __name__ == '__main__':
    app.run(debug=True)
