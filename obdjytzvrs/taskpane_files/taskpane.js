Office.onReady(async (info) => {
    if (info.host === Office.HostType.Word) {
        document.getElementById("sideload-msg").style.display = "none";
        document.getElementById("app-body").style.display = "flex";
        document.getElementById("run").addEventListener('click', readDataFromWord);
    }
});

async function readDataFromWord() {
try {
toggleProcessingStatus(true);

await Word.run(async (context) => {
    const body = context.document.body;
    context.load(body, 'text');
    await context.sync();

    const text_data = body.text;

    // Send data to Flask server
    const response = await fetch('https://127.0.0.1:5004/data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: text_data })
    });
    // document.getElementById("displayText").value =  '.hi there';
    console.log('Data received from Flask server:', response);

    if (response instanceof Response && response.ok) {
        const data = await response.json();
        console.log('Data received from Flask server:', data);

        // Update HTML content with processed data
        const displayText = document.getElementById("displayText");
        displayText.rows = data.processed_text.split("\n").length;
        displayText.value = data.processed_text;
    } else {
        console.error('Failed to send data to Flask server:', response.status);
        document.getElementById("displayText").value = "Error: Failed to send data to Flask server.";
    }
});
} catch (error) {
console.error("Error reading data from Word:", error);
document.getElementById("displayText").value = "Error: " + error.message + error;
} finally {
toggleProcessingStatus(false);
}
}

function toggleProcessingStatus(show) {
    const processingStatusElement = document.getElementById('processingStatus');
    if (show) {
        processingStatusElement.style.display = 'block';
    } else {
        processingStatusElement.style.display = 'none';
    }
}