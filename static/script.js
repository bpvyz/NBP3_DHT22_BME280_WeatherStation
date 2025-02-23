document.getElementById('datePicker').addEventListener('change', function () {
    updateCharts(this.value);
});

async function fetchData(date) {
    const response = await fetch(`/data?date=${date}`);
    return await response.json();
}

async function updateCharts(date) {
    const data = await fetchData(date);

    const labels = data.map(entry => new Date(entry.time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
    const temperatures = data.map(entry => entry.temperature);
    const humidities = data.map(entry => entry.humidity);
    const airQualities = data.map(entry => entry.air_quality);

    new Chart(document.getElementById('combinedChart'), {
        type: 'line',
        data: {
            labels,
            datasets: [
                {
                    label: 'Temperature (°C)',
                    data: temperatures,
                    borderColor: '#FF5733',
                    backgroundColor: 'rgba(255, 87, 51, 0.2)',
                    borderWidth: 3,
                    pointRadius: 5,
                    pointBackgroundColor: '#FF5733',
                    fill: true,
                    tension: 0.3
                },
                {
                    label: 'Humidity (%)',
                    data: humidities,
                    borderColor: '#33C1FF',
                    backgroundColor: 'rgba(51, 193, 255, 0.2)',
                    borderWidth: 3,
                    pointRadius: 5,
                    pointBackgroundColor: '#33C1FF',
                    fill: true,
                    tension: 0.3
                },
                {
                    label: 'Air Quality',
                    data: airQualities,
                    borderColor: '#66FF66',
                    backgroundColor: 'rgba(102, 255, 102, 0.2)',
                    borderWidth: 3,
                    pointRadius: 5,
                    pointBackgroundColor: '#66FF66',
                    fill: true,
                    tension: 0.3
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Weather Data for Today',
                    font: {
                        size: 20,
                        weight: 'bold'
                    },
                    color: '#fff'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(0,0,0,0.7)',
                    titleFont: {
                        size: 14
                    },
                    bodyFont: {
                        size: 12
                    }
                },
                legend: {
                    position: 'top',
                    labels: {
                        font: {
                            size: 14
                        },
                        color: '#fff'
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Time',
                        font: {
                            size: 14
                        },
                        color: '#fff'
                    },
                    grid: {
                        color: '#444',
                        lineWidth: 1
                    },
                    ticks: {
                        color: '#fff'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Values',
                        font: {
                            size: 14
                        },
                        color: '#fff'
                    },
                    grid: {
                        color: '#444',
                        lineWidth: 1
                    },
                    ticks: {
                        beginAtZero: false,
                        callback: function(value) {
                            return value.toFixed(2); // Show 2 decimal points for better precision
                        },
                        color: '#fff'
                    }
                }
            }
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('datePicker').value = today;
    updateCharts(today);
});
