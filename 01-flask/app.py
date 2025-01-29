from flask import Flask, request, render_template, jsonify, session
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Route: Home Page
@app.route('/')
def home():
    return render_template('index.html')

# Route: Upload File
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ['.csv', '.xlsx']:
        return jsonify({'error': 'Invalid file format. Please upload CSV or Excel files.'}), 400

    if file_ext == '.csv':
        data = pd.read_csv(file)
    else:
        data = pd.read_excel(file)

    # Ensure required columns exist
    required_columns = ['SKU Reference No.', 'Tracking Number*', 'Product Name', 'Quantity']
    if not all(col in data.columns for col in required_columns):
        return jsonify({'error': f'Missing columns. Required: {required_columns}'}), 400

    # Save data in session for later use
    session['data'] = data.to_dict(orient='records')
    return jsonify({'message': 'File uploaded successfully'}), 200

# Route: Check AWB
@app.route('/check_awb', methods=['POST'])
def check_awb():
    data = session.get('data', [])
    awb_number = request.json.get('awb_number')

    filtered_data = [item for item in data if item['Tracking Number*'] == awb_number]
    if filtered_data:
        session['current_awb'] = awb_number
        session['remaining_items'] = {item['SKU Reference No.']: item['Quantity'] for item in filtered_data}
        return jsonify({'items': filtered_data}), 200

    return jsonify({'error': 'AWB not found'}), 404

# Route: Check Item Barcode
@app.route('/check_item', methods=['POST'])
def check_item():
    remaining_items = session.get('remaining_items', {})
    item_barcode = request.json.get('item_barcode')

    if item_barcode in remaining_items:
        remaining_items[item_barcode] -= 1
        if remaining_items[item_barcode] <= 0:
            del remaining_items[item_barcode]

        session['remaining_items'] = remaining_items

        if not remaining_items:
            return jsonify({'message': 'All items scanned!'}), 200

        return jsonify({'message': f'Item {item_barcode} scanned successfully'}), 200

    return jsonify({'error': 'Item barcode not found or already scanned'}), 404

if __name__ == '__main__':
    app.run(debug=True)
