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
Note: On first run, the application will automatically train and save the machine learning model using the provided dataset. This may take a few moments.

4. Open your web browser and navigate to:
```
http://127.0.0.1:5000/
```

## Windows Setup Instructions

1. Clone or download this repository to your computer.
2. Open a terminal (Command Prompt or PowerShell) in the project directory.
3. (Recommended) Create and activate a virtual environment:
   ```
   python -m venv .venv
   .venv\Scripts\activate
   ```
4. Install all required packages:
   ```
   pip install -r requirements.txt
   ```
5. Run the Flask app:
   ```
   python app.py
   ```
6. Open your web browser and go to:
   ```
   http://127.0.0.1:5000/
   ```

## Usage Guide (Updated)

- The app uses the built-in `Cleaner_EV_Charging_Stations_3.csv` file for all graphs.
- On the main page, select a graph/chart from the dropdown and click "Show Graph".
- The graph will appear below the button.
- The top right shows the total number of chargers in the USA (from the dataset) and a "+1" button to increment the number live (for fun/demo only).

## Notes
- If you see an error about missing packages (like `matplotlib` or `seaborn`), run:
  ```
  pip install matplotlib seaborn
  ```
- If you see a warning about "DtypeWarning: Columns (5) have mixed types," you can ignore it.
- The app is for local/demo use. For production, use a production WSGI server.

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