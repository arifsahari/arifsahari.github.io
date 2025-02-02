
// 1. File Upload Button – Inserts into MySQL
document.getElementById('uploadButton').onclick = async () => {
    const fileInput = document.getElementById('fileInput');
    if (!fileInput.files.length) return alert('Please upload a file.');

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    const response = await fetch('/upload_file', {
        method: 'POST',
        body: formData
    });
    const result = await response.json();
    if(response.ok){
        alert(result.message);
    } else {
        alert("Upload failed: " + result.error);
    }
};


// 2. Parent Record Search (Using a Textbox)
document.getElementById('parentInput').onchange = async (e) => {
    const query = e.target.value;
    const response = await fetch('/search_parent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query })
    });
    const result = await response.json();
    if(response.ok){
        const parentResults = document.getElementById('parentResults');
        parentResults.innerHTML = '';
        result.records.forEach(record => {
            const row = `<div data-id="${record.id}">
                <p>${record.product_name} (Qty: ${record.quantity})</p>
                <input type="text" class="childInput" placeholder="Enter scanned quantity" />
            </div>`;
            parentResults.innerHTML += row;
        });
    } else {
        alert(result.error);
    }
};


// 3. Child Record Check – Verify Quantity
document.getElementById('parentResults').addEventListener('change', async function(e) {
    if(e.target && e.target.classList.contains('childInput')){
        const scannedQty = e.target.value;
        const parentDiv = e.target.closest('div[data-id]');
        const recordId = parentDiv.getAttribute('data-id');

        const response = await fetch('/check_child', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ record_id: recordId, scanned_qty: scannedQty })
        });
        const result = await response.json();
        alert(result.message);

        // Optionally, update your checking counters here (e.g., increment correct/incorrect counts)
        // Clear the input field after each check
        e.target.value = '';
    }
});


// 4. Maintaining a Checking Counter
let totalChecks = 0;
let correctChecks = 0;
let incorrectChecks = 0;

async function handleChildCheck(e) {
    const scannedQty = e.target.value;
    const parentDiv = e.target.closest('div[data-id]');
    const recordId = parentDiv.getAttribute('data-id');

    const response = await fetch('/check_child', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ record_id: recordId, scanned_qty: scannedQty })
    });
    const result = await response.json();
    totalChecks++;
    if(result.message.includes("correct")){
        correctChecks++;
        alert("Correct! " + result.message);
    } else {
        incorrectChecks++;
        alert("Warning: " + result.message);
    }
    // Update counters display if needed
    document.getElementById('checkCounter').textContent =
         `Total: ${totalChecks}, Correct: ${correctChecks}, Incorrect: ${incorrectChecks}`;
    e.target.value = '';
}

document.getElementById('parentResults').addEventListener('change', function(e) {
    if(e.target && e.target.classList.contains('childInput')){
         handleChildCheck(e);
    }
});
