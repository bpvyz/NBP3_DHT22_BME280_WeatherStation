document.getElementById('datePicker').addEventListener('change', function () {
    updateCharts(this.value);
});

// Store the chart instance globally to destroy it before creating a new one
let chartInstance = null;
let previousDate = document.getElementById('datePicker').value; // Store the initial date value

// Custom alert implementation
function CustomAlert() {
    this.alert = function (message, title) {
        // Create the overlay and dialog box
        const overlay = document.createElement('div');
        overlay.id = 'dialogoverlay';
        overlay.style.height = window.innerHeight + "px";
        document.body.appendChild(overlay);

        const dialogBox = document.createElement('div');
        dialogBox.id = 'dialogbox';
        dialogBox.className = 'slit-in-vertical';
        dialogBox.innerHTML = `
            <div>
                <div id="dialogboxhead"></div>
                <div id="dialogboxbody"></div>
                <div id="dialogboxfoot"></div>
            </div>
        `;
        document.body.appendChild(dialogBox);

        let dialogoverlay = document.getElementById('dialogoverlay');
        let dialogbox = document.getElementById('dialogbox');

        dialogoverlay.style.display = "block";
        dialogbox.style.display = "block";
        dialogbox.style.top = "50%";

        // Set the heading of the alert box
        if (typeof title === 'undefined') {
            document.getElementById('dialogboxhead').style.display = 'none';
        } else {
            document.getElementById('dialogboxhead').innerHTML = '<i class="fa fa-exclamation-circle" aria-hidden="true"></i> ' + title;
        }

        // Set the message of the alert box
        document.getElementById('dialogboxbody').innerHTML = message;

        // Add the footer button to dismiss the alert
        document.getElementById('dialogboxfoot').innerHTML = '<button class="pure-material-button-contained active" onclick="customAlert.ok()">OK</button>';
    };

    this.ok = function () {
        // Remove the modal dialog and overlay when the OK button is clicked
        document.getElementById('dialogbox').style.display = "none";
        document.getElementById('dialogoverlay').style.display = "none";
    };
}

let customAlert = new CustomAlert();

// Fetch data from the server
async function fetchData(date) {
    try {
        const response = await fetch(`/data?date=${date}`);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error("Error fetching data:", error);
        customAlert.alert('Failed to fetch data. Please try again.', 'Error');
        return null;
    }
}

// Update the charts with new data
async function updateCharts(date) {
    const data = await fetchData(date);

    // If no data is available, show an alert and revert to the previous date
    if (!data || data.length === 0) {
        console.warn("No data available for the selected date:", date);
        customAlert.alert('No data available for the selected date. Please try another date.', 'No Data Available');
        document.getElementById('datePicker').value = previousDate; // Revert to the previous date
        return;
    }

    // Save the current date as the previous date
    previousDate = date;

    // Extract data for the chart
    const labels = data.map(entry => new Date(entry.time).toLocaleTimeString('sr-RS', { hour: '2-digit', minute: '2-digit' }));
    const temperatures = data.map(entry => entry.temperature);
    const humidities = data.map(entry => entry.humidity);
    const airQualities = data.map(entry => entry.air_quality);

    const ctx = document.getElementById('combinedChart').getContext('2d');

    // Destroy the old chart if it exists
    if (chartInstance) {
        chartInstance.destroy();
    }

    // Create a new chart
    chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels,
            datasets: [
                {
                    label: 'Temperature (°C)',
                    data: temperatures,
                    borderColor: 'red',
                    backgroundColor: 'rgba(255, 0, 0, 0.2)',
                    fill: true
                },
                {
                    label: 'Humidity (%)',
                    data: humidities,
                    borderColor: 'blue',
                    backgroundColor: 'rgba(0, 0, 255, 0.2)',
                    fill: true
                },
                {
                    label: 'Air Quality',
                    data: airQualities,
                    borderColor: 'green',
                    backgroundColor: 'rgba(0, 255, 0, 0.2)',
                    fill: true
                }
            ]
        },
        options: {
            interaction: {
                intersect: false,
                mode: 'index',
            },
            responsive: true,
            plugins: {
                legend: {
                    labels: { color: 'white' }
                },
            },
            scales: {
                x: { ticks: { color: 'white' } },
                y: { ticks: { color: 'white' }, beginAtZero: false }
            }
        }
    });
}

// Delete data for the selected date
async function deleteData() {
    const date = document.getElementById('datePicker').value;
    if (!date) {
        customAlert.alert('Please select a date first.', 'Error');
        return;
    }

    if (confirm(`Are you sure you want to delete data for ${date}?`)) {
        try {
            const response = await fetch('/delete', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ date: date }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const result = await response.json();
            customAlert.alert(result.message, 'Success');
            updateCharts(date); // Refresh the chart after deletion
        } catch (error) {
            console.error("Error deleting data:", error);
            customAlert.alert('Failed to delete data. Please try again.', 'Error');
        }
    }
}

// Delete all data
async function deleteAllData() {
    if (confirm("Are you sure you want to delete ALL data? This action cannot be undone.")) {
        try {
            const response = await fetch('/delete-all', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const result = await response.json();
            customAlert.alert(result.message, 'Success');

            // Refresh the chart with today's date after deletion
            const today = new Date().toISOString().split('T')[0];
            datePicker.value = today;
            updateCharts(today);
        } catch (error) {
            console.error("Error deleting all data:", error);
            customAlert.alert('Failed to delete all data. Please try again.', 'Error');
        }
    }
}

// Initialize the page with today's date
document.addEventListener('DOMContentLoaded', () => {
    const today = new Date().toISOString().split('T')[0]; // Date in YYYY-MM-DD format
    document.getElementById('datePicker').value = today; // Set today's date in the date picker
    previousDate = today; // Save the initial date when the page loads
    updateCharts(today);
});