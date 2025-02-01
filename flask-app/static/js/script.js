document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('uploadButton').onclick = async () => {
        const fileInput = document.getElementById('fileInput');
        if (!fileInput.files.length) return alert('Please upload a file.');

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        alert(result.message || result.error);
    };

    document.getElementById('awbInput').onchange = async (e) => {
        const awbNumber = e.target.value;
        const response = await fetch('/check_awb', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ awb_number: awbNumber })
        });

        const result = await response.json();
        if (response.ok) {
            document.getElementById('awbDisplay').textContent = awbNumber;
            const itemsTable = document.getElementById('itemsTable');
            itemsTable.innerHTML = '';
            result.items.forEach(item => {
                const row = `<tr>
                    <td>${item['SKU Reference No.']}</td>
                    <td>${item['Product Name']}</td>
                    <td>${item['Quantity']}</td>
                </tr>`;
                itemsTable.innerHTML += row;
            });

            document.getElementById('awbSection').style.display = 'none';
            document.getElementById('itemsSection').style.display = 'block';

            // Auto-focus on item input
            document.getElementById('itemInput').focus();
        } else {
            alert(result.error);
        }
    };

    document.getElementById('itemInput').onchange = async (e) => {
        const itemBarcode = e.target.value;
        const response = await fetch('/check_item', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ item_barcode: itemBarcode })
        });

        const result = await response.json();
        alert(result.message || result.error);

        e.target.value = '';  // Clear input after scanning

        if (result.message && result.message.includes('All items scanned')) {
            document.getElementById('awbSection').style.display = 'block';
            document.getElementById('itemsSection').style.display = 'none';
            document.getElementById('awbInput').value = ''; // Clear AWB input
            document.getElementById('awbInput').focus(); // Focus back to AWB input
        } else {
            document.getElementById('itemInput').focus(); // Focus back to item input
        }
    };
});
