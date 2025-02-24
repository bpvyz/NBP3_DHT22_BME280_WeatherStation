document.getElementById('datePicker').addEventListener('change', function () {
    updateCharts(this.value);
});

// Čuvamo instancu grafa globalno da bismo ga uništili pre kreiranja novog
let chartInstance = null;
let previousDate = document.getElementById('datePicker').value; // Store the initial date value

async function fetchData(date) {
    const response = await fetch(`/data?date=${date}`);
    return await response.json();
}

async function updateCharts(date) {
    const data = await fetchData(date);

    // Ako nema podataka, prikazujemo custom alert
    if (!data || data.length === 0) {
        console.warn("No data available for the selected date:", date);
        customAlert.alert('No data available for the selected date. Please try another date.', 'No Data Available');
        // Restore the previous date after the alert is shown
        document.getElementById('datePicker').value = previousDate;
        return;
    }

    previousDate = document.getElementById('datePicker').value;
    const labels = data.map(entry => new Date(entry.time).toLocaleTimeString('sr-RS', { hour: '2-digit', minute: '2-digit' }));
    const temperatures = data.map(entry => entry.temperature);
    const humidities = data.map(entry => entry.humidity);
    const airQualities = data.map(entry => entry.air_quality);

    const ctx = document.getElementById('combinedChart').getContext('2d');

    // Uništimo stari graf ako postoji
    if (chartInstance) {
        chartInstance.destroy();
    }

    // Kreiramo novi graf
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

function CustomAlert(){
  this.alert = function(message, title){
    // Create the overlay and dialog box without modifying the entire body
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
  }

  this.ok = function(){
    // Remove the modal dialog and overlay when the OK button is clicked
    document.getElementById('dialogbox').style.display = "none";
    document.getElementById('dialogoverlay').style.display = "none";
  }
}

let customAlert = new CustomAlert();

document.addEventListener('DOMContentLoaded', () => {
    const today = new Date().toISOString().split('T')[0]; // Date in YYYY-MM-DD format
    document.getElementById('datePicker').value = today; // Set today's date in the date picker
    previousDate = today;  // Save the initial date when page loads
    updateCharts(today);
});
