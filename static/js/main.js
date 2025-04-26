// Input validation
function validateCoordinates(lat, lon) {
    if (isNaN(lat) || isNaN(lon)) {
        return "Latitude and longitude must be numbers";
    }
    if (lat < -90 || lat > 90) {
        return "Latitude must be between -90 and 90";
    }
    if (lon < -180 || lon > 180) {
        return "Longitude must be between -180 and 180";
    }
    return null;
}

// Format numbers with commas
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Load states on page load
async function loadStates() {
    try {
        const response = await fetch('/get_states');
        const states = await response.json();
        
        const stateSelect = document.getElementById('stateSelect');
        states.forEach(state => {
            const option = document.createElement('option');
            option.value = state;
            option.textContent = state;
            stateSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading states:', error);
    }
}

// Load cities when state is selected
async function loadCities() {
    const state = document.getElementById('stateSelect').value;
    const citySelect = document.getElementById('citySelect');
    
    // Reset and disable city select if no state selected
    if (!state) {
        citySelect.innerHTML = '<option value="">Select a city...</option>';
        citySelect.disabled = true;
        return;
    }
    
    try {
        // Update map for state view
        await updateMap(state);
        
        const response = await fetch(`/get_cities/${encodeURIComponent(state)}`);
        const cities = await response.json();
        
        citySelect.innerHTML = '<option value="">Select a city...</option>';
        cities.forEach(city => {
            const option = document.createElement('option');
            option.value = city;
            option.textContent = city;
            citySelect.appendChild(option);
        });
        citySelect.disabled = false;
    } catch (error) {
        console.error('Error loading cities:', error);
        citySelect.innerHTML = '<option value="">Error loading cities</option>';
        citySelect.disabled = true;
    }
}

// Update map when city is selected
async function onCitySelect() {
    const state = document.getElementById('stateSelect').value;
    const city = document.getElementById('citySelect').value;
    
    if (state && city) {
        await updateMap(state, city);
    }
}

// Function to update the map
async function updateMap(state, city = null) {
    try {
        const response = await fetch(`/update_map?state=${encodeURIComponent(state)}${city ? `&city=${encodeURIComponent(city)}` : ''}`);
        if (!response.ok) {
            throw new Error('Failed to update map');
        }
        
        // Refresh the map iframe
        const mapFrame = document.querySelector('.map-frame');
        mapFrame.src = mapFrame.src;
    } catch (error) {
        console.error('Error updating map:', error);
    }
}

// Prediction function
async function predict() {
    const state = document.getElementById('stateSelect').value;
    const city = document.getElementById('citySelect').value;
    const predictionDiv = document.getElementById('prediction');
    
    if (!state || !city) {
        predictionDiv.innerHTML = `
            <div class="alert alert-warning">
                Please select both state and city
            </div>
        `;
        return;
    }
    
    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ state, city })
        });
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        
        const data = await response.json();
        
        if (data.error) {
            predictionDiv.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
            return;
        }
        
        // Display prediction and actual statistics
        let html = `
            <div class="card mb-3">
                <div class="card-body">
                    <h6 class="card-title">Current Statistics</h6>
                    <p class="mb-1">Existing Charging Stations: ${formatNumber(data.actual_stations)}</p>
                    <p class="mb-1">Total Existing Chargers: ${formatNumber(data.actual_chargers)}</p>
                    <hr>
                    <h6 class="card-title">Model Prediction</h6>
                    <p class="mb-1">Predicted Number of Chargers: ${formatNumber(Math.round(data.predicted_chargers))}</p>
                    <small class="text-muted">
                        This prediction is based on geographical patterns and may differ from actual numbers
                        due to various local factors.
                    </small>
                </div>
            </div>
        `;
        
        if (data.nearby_stations && data.nearby_stations.length > 0) {
            html += `
                <h6>Nearby Stations (within 15 miles):</h6>
                <div class="list-group">
            `;
            
            data.nearby_stations.forEach(station => {
                html += `
                    <div class="list-group-item">
                        <div class="d-flex justify-content-between align-items-start">
                            <div>
                                <h6 class="mb-1">${station['Station Name']}</h6>
                                <p class="mb-1">${station['Street Address']}</p>
                                <p class="mb-1">${station['City']}, ${station['State']}</p>
                                <small>Total Chargers: ${station['Total_Chargers']}</small>
                            </div>
                            <span class="badge bg-primary rounded-pill">${station['Distance']}</span>
                        </div>
                    </div>
                `;
            });
            
            html += '</div>';
        } else {
            html += `
                <div class="alert alert-info">
                    No charging stations found within 15 miles.
                </div>
            `;
        }
        
        predictionDiv.innerHTML = html;
        
    } catch (error) {
        predictionDiv.innerHTML = `
            <div class="alert alert-danger">
                Error making prediction. Please try again later.
            </div>
        `;
        console.error('Error:', error);
    }
}

// Search function
async function searchStations() {
    const query = document.getElementById('searchInput').value.trim();
    const resultsDiv = document.getElementById('searchResults');
    
    if (!query) {
        resultsDiv.innerHTML = `
            <div class="alert alert-warning">
                Please enter a search term
            </div>
        `;
        return;
    }
    
    try {
        const response = await fetch(`/search?q=${encodeURIComponent(query)}`);
        const data = await response.json();
        
        if (!data.length) {
            resultsDiv.innerHTML = `
                <div class="alert alert-info">
                    No locations found matching "${query}"
                </div>
            `;
            return;
        }
        
        let html = '';
        data.forEach(result => {
            if (result.type === 'State') {
                // State result with top cities
                html += `
                    <div class="card mb-3">
                        <div class="card-header bg-primary text-white">
                            <h6 class="mb-0">${result.name} State Summary</h6>
                        </div>
                        <div class="card-body">
                            <p class="mb-2">
                                <strong>Total Stations:</strong> ${formatNumber(result.total_stations)}<br>
                                <strong>Total Chargers:</strong> ${formatNumber(result.total_chargers)}
                            </p>
                            <h6 class="mb-2">Top Cities:</h6>
                            <div class="list-group">
                `;
                
                result.top_cities.forEach(city => {
                    html += `
                        <div class="list-group-item">
                            <div class="d-flex justify-content-between align-items-center">
                                <h6 class="mb-1">${city.name}</h6>
                                <span class="badge bg-success">${formatNumber(city.total_chargers)} chargers</span>
                            </div>
                            <small>Stations: ${formatNumber(city.total_stations)}</small>
                        </div>
                    `;
                });
                
                html += `
                            </div>
                        </div>
                    </div>
                `;
            } else {
                // Individual city result
                html += `
                    <div class="list-group-item">
                        <div class="d-flex justify-content-between align-items-center">
                            <h6 class="mb-1">${result.name}</h6>
                            <span class="badge bg-success">${formatNumber(result.total_chargers)} chargers</span>
                        </div>
                        <small>Stations: ${formatNumber(result.total_stations)}</small>
                    </div>
                `;
            }
        });
        
        resultsDiv.innerHTML = html;
        
    } catch (error) {
        resultsDiv.innerHTML = `
            <div class="alert alert-danger">
                Error performing search. Please try again later.
            </div>
        `;
        console.error('Error:', error);
    }
}

// Add event listeners
document.getElementById('searchInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        searchStations();
    }
});

// Add event listener for city selection
document.getElementById('citySelect').addEventListener('change', onCitySelect);

// Load states when page loads
document.addEventListener('DOMContentLoaded', loadStates); 