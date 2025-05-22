document.addEventListener('DOMContentLoaded', function() {
    // Initialize map if map container exists
    const mapContainer = document.getElementById('food-bank-map');
    if (mapContainer) {
        initializeMap(mapContainer);
    }
});

function initializeMap(container) {
    // Create map centered on a default location (adjust as needed)
    const map = L.map(container).setView([40.7128, -74.0060], 10);
    
    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
    
    // Get food bank locations from data attribute
    const foodBanksData = container.dataset.locations;
    let foodBanks = [];
    
    try {
        foodBanks = JSON.parse(foodBanksData);
    } catch (e) {
        console.error('Error parsing food bank data:', e);
        return;
    }
    
    // Add markers for each food bank
    const markers = [];
    foodBanks.forEach(foodBank => {
        if (foodBank.latitude && foodBank.longitude) {
            const marker = L.marker([foodBank.latitude, foodBank.longitude])
                .addTo(map)
                .bindPopup(`
                    <strong>${foodBank.name}</strong><br>
                    ${foodBank.address}<br>
                    ${foodBank.city}, ${foodBank.state} ${foodBank.zip_code}<br>
                    <a href="tel:${foodBank.phone}">${foodBank.phone}</a><br>
                    <a href="/locations/${foodBank.id}" class="btn btn-sm btn-primary mt-2">View Details</a>
                `);
            
            markers.push(marker);
        }
    });
    
    // Fit map to show all markers if there are any
    if (markers.length > 0) {
        const group = new L.featureGroup(markers);
        map.fitBounds(group.getBounds().pad(0.1));
    }
    
    // Add geolocation control
    L.control.locate({
        position: 'topright',
        strings: {
            title: "Show my location"
        }
    }).addTo(map);
}

function getDirections(foodBankId) {
    // Get food bank details
    fetch(`/locations/${foodBankId}/details`)
        .then(response => response.json())
        .then(data => {
            // Try to get user's current location
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(position => {
                    const userLat = position.coords.latitude;
                    const userLng = position.coords.longitude;
                    
                    // Open directions in Google Maps
                    const destinationCoords = `${data.latitude},${data.longitude}`;
                    const url = `https://www.google.com/maps/dir/?api=1&origin=${userLat},${userLng}&destination=${destinationCoords}`;
                    window.open(url, '_blank');
                }, error => {
                    // If geolocation fails, just open the food bank location
                    const url = `https://www.google.com/maps/search/?api=1&query=${data.latitude},${data.longitude}`;
                    window.open(url, '_blank');
                    console.error('Geolocation error:', error);
                });
            } else {
                // Fallback if geolocation is not supported
                const url = `https://www.google.com/maps/search/?api=1&query=${data.latitude},${data.longitude}`;
                window.open(url, '_blank');
            }
        })
        .catch(error => {
            console.error('Error getting food bank details:', error);
            alert('Unable to get directions at this time.');
        });
}

function showLocationDetails(foodBankId) {
    // Redirect to food bank details page
    window.location.href = `/locations/${foodBankId}`;
}

function optimizeRoute(distributionId) {
    // Get distribution event details and beneficiary locations
    fetch(`/distribution/${distributionId}/route-data`)
        .then(response => response.json())
        .then(data => {
            const map = L.map('route-map').setView([data.center.latitude, data.center.longitude], 12);
            
            // Add OpenStreetMap tiles
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            }).addTo(map);
            
            // Add food bank marker
            const foodBankMarker = L.marker([data.foodBank.latitude, data.foodBank.longitude], {
                icon: L.divIcon({
                    className: 'food-bank-marker',
                    html: '<i class="fas fa-warehouse"></i>',
                    iconSize: [30, 30]
                })
            })
            .addTo(map)
            .bindPopup(`<strong>Start: ${data.foodBank.name}</strong>`);
            
            // Add beneficiary markers
            const markers = [];
            data.beneficiaries.forEach((beneficiary, index) => {
                const marker = L.marker([beneficiary.latitude, beneficiary.longitude], {
                    icon: L.divIcon({
                        className: 'beneficiary-marker',
                        html: `<div class="number-marker">${index + 1}</div>`,
                        iconSize: [20, 20]
                    })
                })
                .addTo(map)
                .bindPopup(`<strong>Stop ${index + 1}</strong><br>${beneficiary.address}`);
                
                markers.push(marker);
            });
            
            // Draw route line if route data is provided
            if (data.route && data.route.coordinates) {
                const routeLine = L.polyline(data.route.coordinates, {
                    color: 'blue',
                    weight: 3,
                    opacity: 0.7
                }).addTo(map);
            }
            
            // Fit map to show all markers
            const allMarkers = [foodBankMarker, ...markers];
            const group = new L.featureGroup(allMarkers);
            map.fitBounds(group.getBounds().pad(0.1));
            
            // Display route information
            const routeInfo = document.getElementById('route-info');
            if (routeInfo) {
                routeInfo.innerHTML = `
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">Route Information</h5>
                            <p>Total Distance: ${data.route.distance} miles</p>
                            <p>Estimated Time: ${data.route.duration}</p>
                            <p>Number of Stops: ${data.beneficiaries.length}</p>
                        </div>
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Error loading route data:', error);
            alert('Unable to optimize route at this time.');
        });
}
