# EV Charging Station Predictor

This web application provides comprehensive information about electric vehicle charging stations across the United States, featuring interactive visualization, search capabilities, and machine learning predictions for charging infrastructure.

## Features

### Interactive Map Visualization
- Dynamic map showing charging station locations across the US
- Color-coded markers indicating charging station density
- Interactive markers with detailed station information
- Automatic map focus when selecting states or cities
- Custom EV charger icons for better visibility

### Search Capabilities
- Search for charging stations by state, city, or station name
- View aggregated statistics for states and cities
- See top 10 cities with most chargers in each state
- Detailed station information including:
  - Total number of stations
  - Total number of chargers
  - Station addresses and locations

### Prediction System
- Predict potential number of chargers for selected locations
- Compare predictions with actual current infrastructure
- View nearby stations within 15 miles
- Distance calculations in miles for US-based users

### Real-time Updates
- Interactive state and city selection
- Map automatically updates to focus on selected areas
- Instant display of nearby charging stations
- Current statistics vs. predictions comparison

## Setup Instructions

1. Create a virtual environment (recommended):
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open your web browser and navigate to:
```
http://127.0.0.1:5000/
```

## Usage Guide

### 1. Exploring the Map
- Initial view shows nationwide charging station distribution
- Color-coded points indicate charging station density:
  - Green: Low density
  - Blue: Medium-low density
  - Purple: Medium density
  - Orange: Medium-high density
  - Red: High density
- Click on any point to see station details

### 2. Searching for Locations
- Use the search box to find stations by:
  - State name
  - City name
  - Station name
- Results show:
  - Total number of stations
  - Total number of chargers
  - Top cities (for state searches)

### 3. Making Predictions
1. Select a state from the dropdown
   - Map automatically updates to show state view
   - View all charging stations in the selected state
2. Select a city from the dropdown
   - Map zooms to city location
   - Shows nearby charging stations
3. View prediction results:
   - Current statistics
   - Predicted number of chargers
   - List of nearby stations within 15 miles

### 4. Viewing Station Details
- Each station marker shows:
  - Station name
  - Street address
  - City and state
  - Total number of chargers
  - Distance from selected location (when applicable)

## Data Sources

- EV Charging Station data from February 2024
- Comprehensive coverage of charging stations across the United States
- Regular updates to maintain data accuracy

## Model Information

The application uses a Random Forest Regressor model to predict charging station numbers:
- Takes geographical location as input
- Uses standardized features for prediction
- Trained on actual charging station data
- Provides predictions based on geographical patterns and infrastructure density

## Requirements

See `requirements.txt` for a complete list of dependencies. Key packages include:
- Flask for web framework
- Pandas for data handling
- Scikit-learn for machine learning
- Folium for map visualization
- NumPy for numerical operations 