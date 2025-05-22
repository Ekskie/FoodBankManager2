// Chart initialization functions
function setupInventoryChart(canvas) {
    // Get inventory data from data attribute
    const data = JSON.parse(canvas.getAttribute('data-chart-values'));
    
    new Chart(canvas, {
        type: 'pie',
        data: {
            labels: data.categories,
            datasets: [{
                data: data.quantities,
                backgroundColor: [
                    'rgba(255, 99, 132, 0.7)',
                    'rgba(54, 162, 235, 0.7)',
                    'rgba(255, 206, 86, 0.7)',
                    'rgba(75, 192, 192, 0.7)',
                    'rgba(153, 102, 255, 0.7)',
                    'rgba(255, 159, 64, 0.7)',
                    'rgba(199, 199, 199, 0.7)',
                    'rgba(83, 102, 255, 0.7)',
                    'rgba(40, 159, 64, 0.7)'
                ],
                borderColor: [
                    'rgb(255, 99, 132)',
                    'rgb(54, 162, 235)',
                    'rgb(255, 206, 86)',
                    'rgb(75, 192, 192)',
                    'rgb(153, 102, 255)',
                    'rgb(255, 159, 64)',
                    'rgb(199, 199, 199)',
                    'rgb(83, 102, 255)',
                    'rgb(40, 159, 64)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                },
                title: {
                    display: true,
                    text: 'Inventory by Category'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100);
                            return `${label}: ${value} items (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

function setupDonationsChart(canvas) {
    // Get donations data from data attribute
    const data = JSON.parse(canvas.getAttribute('data-chart-values'));
    
    new Chart(canvas, {
        type: 'bar',
        data: {
            labels: data.months,
            datasets: [
                {
                    label: 'Food Donations',
                    data: data.foodDonations,
                    backgroundColor: 'rgba(75, 192, 192, 0.7)',
                    borderColor: 'rgb(75, 192, 192)',
                    borderWidth: 1
                },
                {
                    label: 'Monetary Donations ($)',
                    data: data.monetaryDonations,
                    backgroundColor: 'rgba(153, 102, 255, 0.7)',
                    borderColor: 'rgb(153, 102, 255)',
                    borderWidth: 1,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Month'
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Food Donations (Count)'
                    }
                },
                y1: {
                    position: 'right',
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Monetary Donations ($)'
                    },
                    grid: {
                        drawOnChartArea: false
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Donations Over Time'
                },
                legend: {
                    position: 'top'
                }
            }
        }
    });
}

function setupVolunteerHoursChart(canvas) {
    // Get volunteer hours data from data attribute
    const data = JSON.parse(canvas.getAttribute('data-chart-values'));
    
    new Chart(canvas, {
        type: 'line',
        data: {
            labels: data.weeks,
            datasets: [{
                label: 'Volunteer Hours',
                data: data.hours,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgb(54, 162, 235)',
                borderWidth: 2,
                tension: 0.1,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Week'
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Hours'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Volunteer Hours per Week'
                }
            }
        }
    });
}

function setupBeneficiariesChart(canvas) {
    // Get beneficiary data from data attribute
    const data = JSON.parse(canvas.getAttribute('data-chart-values'));
    
    new Chart(canvas, {
        type: 'doughnut',
        data: {
            labels: ['Pending', 'Approved', 'Fulfilled', 'Declined'],
            datasets: [{
                data: [
                    data.requestsByStatus.pending,
                    data.requestsByStatus.approved,
                    data.requestsByStatus.fulfilled,
                    data.requestsByStatus.declined
                ],
                backgroundColor: [
                    'rgba(255, 206, 86, 0.7)',
                    'rgba(75, 192, 192, 0.7)',
                    'rgba(54, 162, 235, 0.7)',
                    'rgba(255, 99, 132, 0.7)'
                ],
                borderColor: [
                    'rgb(255, 206, 86)',
                    'rgb(75, 192, 192)',
                    'rgb(54, 162, 235)',
                    'rgb(255, 99, 132)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                },
                title: {
                    display: true,
                    text: 'Food Requests by Status'
                }
            }
        }
    });
}

function setupDistributionChart(canvas) {
    // Get distribution data from data attribute
    const data = JSON.parse(canvas.getAttribute('data-chart-values'));
    
    new Chart(canvas, {
        type: 'bar',
        data: {
            labels: data.foodBanks,
            datasets: [{
                label: 'Distributions Completed',
                data: data.completedCounts,
                backgroundColor: 'rgba(75, 192, 192, 0.7)',
                borderColor: 'rgb(75, 192, 192)',
                borderWidth: 1
            }, {
                label: 'Distributions Planned',
                data: data.plannedCounts,
                backgroundColor: 'rgba(255, 206, 86, 0.7)',
                borderColor: 'rgb(255, 206, 86)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Food Bank'
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Distribution Count'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Distributions by Food Bank'
                },
                legend: {
                    position: 'top'
                }
            }
        }
    });
}

function setupImpactChart(canvas) {
    // Get impact data from data attribute
    const data = JSON.parse(canvas.getAttribute('data-chart-values'));
    
    new Chart(canvas, {
        type: 'radar',
        data: {
            labels: ['Donations Received', 'People Helped', 'Volunteer Hours', 'Meals Provided', 'Events Organized'],
            datasets: [{
                label: 'Current Month',
                data: [
                    data.currentMonth.donations,
                    data.currentMonth.peopleHelped,
                    data.currentMonth.volunteerHours,
                    data.currentMonth.mealsProvided,
                    data.currentMonth.events
                ],
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgb(54, 162, 235)',
                borderWidth: 2,
                pointBackgroundColor: 'rgb(54, 162, 235)',
                pointRadius: 5
            }, {
                label: 'Last Month',
                data: [
                    data.lastMonth.donations,
                    data.lastMonth.peopleHelped,
                    data.lastMonth.volunteerHours,
                    data.lastMonth.mealsProvided,
                    data.lastMonth.events
                ],
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                borderColor: 'rgb(255, 99, 132)',
                borderWidth: 2,
                pointBackgroundColor: 'rgb(255, 99, 132)',
                pointRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Impact Metrics Comparison'
                },
                legend: {
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.dataset.label || '';
                            const value = context.raw || 0;
                            const i = context.dataIndex;
                            
                            // Format based on metric type
                            if (i === 0) return `${label}: ${value} donations`;
                            if (i === 1) return `${label}: ${value} people`;
                            if (i === 2) return `${label}: ${value} hours`;
                            if (i === 3) return `${label}: ${value} meals`;
                            if (i === 4) return `${label}: ${value} events`;
                            
                            return `${label}: ${value}`;
                        }
                    }
                }
            },
            scales: {
                r: {
                    angleLines: {
                        display: true
                    },
                    ticks: {
                        beginAtZero: true
                    }
                }
            }
        }
    });
}
