from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
import folium
from folium import plugins
import joblib
import os
from werkzeug.utils import secure_filename
import matplotlib.pyplot as plt
import seaborn as sns
import uuid
import matplotlib
matplotlib.use('Agg')

app = Flask(__name__)

# Load and preprocess the data
df = pd.read_csv('Cleaner_EV_Charging_Stations_3.csv', encoding='latin1', low_memory=False)

# Aggregate stations by state
state_stats = df.groupby('State').agg({
    'Total_Chargers': 'sum',
    'Station Name': 'count',  # Count of stations
    'Latitude': 'mean',
    'Longitude': 'mean'
}).reset_index()

# Aggregate stations by city
city_stats = df.groupby(['State', 'City']).agg({
    'Total_Chargers': 'sum',
    'Station Name': 'count',  # Count of stations
    'Latitude': 'mean',
    'Longitude': 'mean'
}).reset_index()

def train_and_save_model():
    # Features for prediction
    features = ['Latitude', 'Longitude']
    X = df[features]
    y = df['Total_Chargers']
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_scaled, y)
    
    # Save model and scaler
    if not os.path.exists('static/models'):
        os.makedirs('static/models')
    joblib.dump(model, 'static/models/model.joblib')
    joblib.dump(scaler, 'static/models/scaler.joblib')
    
    return model, scaler

# Load or train model
if os.path.exists('static/models/model.joblib'):
    model = joblib.load('static/models/model.joblib')
    scaler = joblib.load('static/models/scaler.joblib')
else:
    model, scaler = train_and_save_model()

@app.route('/get_states')
def get_states():
    states = sorted(df['State'].unique().tolist())
    return jsonify(states)

@app.route('/get_cities/<state>')
def get_cities(state):
    cities = sorted(df[df['State'] == state]['City'].unique().tolist())
    return jsonify(cities)

@app.route('/')
def welcome():
    return render_template('main.html', total_chargers=0)

@app.route('/wack')
def home():
    # Create a map centered on the US
    m = folium.Map(
        location=[39.8283, -98.5795],
        zoom_start=4,
        tiles='cartodbpositron'  # Light theme for better visibility
    )
    
    # Get the range of charger counts for color scaling
    max_chargers = state_stats['Total_Chargers'].max()
    
    # Color function to get color based on charger count
    def get_color(charger_count):
        ratio = charger_count / max_chargers
        if ratio < 0.2:
            return 'green'  # Low counts
        elif ratio < 0.4:
            return 'blue'   # Medium-low counts
        elif ratio < 0.6:
            return 'purple' # Medium counts
        elif ratio < 0.8:
            return 'orange' # Medium-high counts
        else:
            return 'red'    # High counts
    
    # Add markers for each state with total chargers
    for _, row in state_stats.iterrows():
        # Skip if we don't have valid coordinates
        if pd.isna(row['Latitude']) or pd.isna(row['Longitude']):
            continue
            
        # Create popup content
        popup_content = f"""
            <div style='width: 200px'>
                <h6 style='margin:0;'>{row['State']}</h6>
                <hr style='margin:4px 0;'>
                <b>Total Chargers:</b> {int(row['Total_Chargers']):,}<br>
                <b>Charging Stations:</b> {int(row['Station Name']):,}
            </div>
        """
        
        # Create custom icon HTML
        icon_color = get_color(row['Total_Chargers'])
        icon = folium.DivIcon(
            html=f"""
                <div style="
                    width: 12px;
                    height: 12px;
                    background-color: {icon_color};
                    border: 2px solid white;
                    border-radius: 50%;
                    box-shadow: 0 0 4px rgba(0,0,0,0.5);
                "></div>
            """
        )
        
        # Add marker
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=folium.Popup(popup_content, max_width=300),
            icon=icon
        ).add_to(m)
    
    # Add a legend
    legend_html = '''
        <div style="position: fixed; bottom: 50px; right: 50px; 
                    width: 180px; background-color: white;
                    border:2px solid grey; z-index:9999; font-size:14px;
                    padding: 10px; border-radius: 5px;">
            <h6 style="margin-top:0;">Charger Density</h6>
            <div style="margin: 2px 0;">
                <span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:green;border:1px solid white;box-shadow:0 0 4px rgba(0,0,0,0.5);"></span>
                <span style="margin-left:5px;">Low</span>
            </div>
            <div style="margin: 2px 0;">
                <span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:blue;border:1px solid white;box-shadow:0 0 4px rgba(0,0,0,0.5);"></span>
                <span style="margin-left:5px;">Medium-Low</span>
            </div>
            <div style="margin: 2px 0;">
                <span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:purple;border:1px solid white;box-shadow:0 0 4px rgba(0,0,0,0.5);"></span>
                <span style="margin-left:5px;">Medium</span>
            </div>
            <div style="margin: 2px 0;">
                <span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:orange;border:1px solid white;box-shadow:0 0 4px rgba(0,0,0,0.5);"></span>
                <span style="margin-left:5px;">Medium-High</span>
            </div>
            <div style="margin: 2px 0;">
                <span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:red;border:1px solid white;box-shadow:0 0 4px rgba(0,0,0,0.5);"></span>
                <span style="margin-left:5px;">High</span>
            </div>
        </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Save map to static folder
    if not os.path.exists('static'):
        os.makedirs('static')
    m.save('static/map.html')
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        state = data['state']
        city = data['city']
        
        # Get actual data for the city
        actual_data = city_stats[
            (city_stats['State'] == state) & 
            (city_stats['City'] == city)
        ].iloc[0]
        
        # Scale input
        input_data = scaler.transform([[actual_data['Latitude'], actual_data['Longitude']]])
        
        # Make prediction
        prediction = model.predict(input_data)[0]
        
        return jsonify({
            'predicted_chargers': prediction,
            'actual_chargers': int(actual_data['Total_Chargers']),
            'actual_stations': int(actual_data['Station Name']),
            'nearby_stations': get_nearby_stations(actual_data['Latitude'], actual_data['Longitude'])
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

def get_nearby_stations(lat, lon, radius=15):  # radius now in miles
    # Calculate distances using Haversine formula
    def haversine_distance(lat1, lon1, lat2, lon2):
        R = 3959  # Earth's radius in miles (instead of 6371 km)
        
        # Convert latitude/longitude to radians
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        distance = R * c
        
        return distance
    
    # Calculate distance for each station
    df['Distance'] = df.apply(
        lambda row: haversine_distance(lat, lon, row['Latitude'], row['Longitude'])
        if not pd.isna(row['Latitude']) and not pd.isna(row['Longitude'])
        else float('inf'),
        axis=1
    )
    
    # Find stations within radius miles, sorted by distance
    nearby = df[df['Distance'] <= radius].sort_values('Distance').head(5)
    
    # Format the results
    results = []
    for _, station in nearby.iterrows():
        results.append({
            'Station Name': station['Station Name'],
            'Street Address': station['Street Address'],
            'City': station['City'],
            'State': station['State'],
            'Total_Chargers': station['Total_Chargers'],
            'Distance': f"{station['Distance']:.1f} mi"
        })
    
    return results

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '').lower()
    
    # Search results container
    results = []
    
    # Search in states
    state_matches = state_stats[
        state_stats['State'].str.lower().str.contains(query)
    ]
    
    for _, state_row in state_matches.iterrows():
        state_result = {
            'type': 'State',
            'name': state_row['State'],
            'total_stations': int(state_row['Station Name']),
            'total_chargers': int(state_row['Total_Chargers']),
            'top_cities': []
        }
        
        # Get top 10 cities for this state
        top_cities = city_stats[
            city_stats['State'] == state_row['State']
        ].nlargest(10, 'Total_Chargers')
        
        for _, city_row in top_cities.iterrows():
            state_result['top_cities'].append({
                'name': city_row['City'],
                'total_stations': int(city_row['Station Name']),
                'total_chargers': int(city_row['Total_Chargers'])
            })
        
        results.append(state_result)
    
    # If no state matches, search for individual cities
    if not results:
        city_matches = city_stats[
            city_stats['City'].str.lower().str.contains(query)
        ].nlargest(10, 'Total_Chargers')
        
        for _, row in city_matches.iterrows():
            results.append({
                'type': 'City',
                'name': f"{row['City']}, {row['State']}",
                'total_stations': int(row['Station Name']),
                'total_chargers': int(row['Total_Chargers'])
            })
    
    return jsonify(results)

@app.route('/get_location_coords', methods=['GET'])
def get_location_coords():
    state = request.args.get('state')
    city = request.args.get('city')
    
    try:
        if city:
            # Get city coordinates
            city_data = city_stats[
                (city_stats['State'] == state) & 
                (city_stats['City'] == city)
            ].iloc[0]
            
            # Get nearby stations for this city
            nearby = df[
                (df['State'] == state) &
                (abs(df['Latitude'] - city_data['Latitude']) < 0.5) &
                (abs(df['Longitude'] - city_data['Longitude']) < 0.5)
            ]
            
            return jsonify({
                'latitude': city_data['Latitude'],
                'longitude': city_data['Longitude'],
                'zoom': 12,
                'stations': nearby[['Station Name', 'Street Address', 'City', 'State', 'Latitude', 'Longitude', 'Total_Chargers']].to_dict('records')
            })
        
        elif state:
            # Get state coordinates
            state_data = state_stats[state_stats['State'] == state].iloc[0]
            
            # Get all stations in this state
            state_stations = df[df['State'] == state]
            
            return jsonify({
                'latitude': state_data['Latitude'],
                'longitude': state_data['Longitude'],
                'zoom': 7,
                'stations': state_stations[['Station Name', 'Street Address', 'City', 'State', 'Latitude', 'Longitude', 'Total_Chargers']].to_dict('records')
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/update_map')
def update_map():
    state = request.args.get('state')
    city = request.args.get('city')
    
    try:
        # Create a new map
        if city:
            # Get city coordinates
            city_data = city_stats[
                (city_stats['State'] == state) & 
                (city_stats['City'] == city)
            ].iloc[0]
            m = folium.Map(
                location=[city_data['Latitude'], city_data['Longitude']],
                zoom_start=12,
                tiles='cartodbpositron'
            )
            
            # Get nearby stations
            nearby = df[
                (df['State'] == state) &
                (abs(df['Latitude'] - city_data['Latitude']) < 0.5) &
                (abs(df['Longitude'] - city_data['Longitude']) < 0.5)
            ]
            
            # Add markers for nearby stations
            for _, station in nearby.iterrows():
                if pd.isna(station['Latitude']) or pd.isna(station['Longitude']):
                    continue
                
                popup_content = f"""
                    <div style='width: 200px'>
                        <h6 style='margin:0;'>{station['Station Name']}</h6>
                        <hr style='margin:4px 0;'>
                        <p style='margin:0;'>{station['Street Address']}</p>
                        <p style='margin:0;'>{station['City']}, {station['State']}</p>
                        <b>Total Chargers:</b> {int(station['Total_Chargers'])}
                    </div>
                """
                
                folium.Marker(
                    location=[station['Latitude'], station['Longitude']],
                    popup=folium.Popup(popup_content, max_width=300),
                    icon=folium.Icon(color='green', icon='plug', prefix='fa')
                ).add_to(m)
                
        else:
            # Get state coordinates
            state_data = state_stats[state_stats['State'] == state].iloc[0]
            m = folium.Map(
                location=[state_data['Latitude'], state_data['Longitude']],
                zoom_start=7,
                tiles='cartodbpositron'
            )
            
            # Get all stations in the state
            state_stations = df[df['State'] == state]
            
            # Add markers for all stations in the state
            for _, station in state_stations.iterrows():
                if pd.isna(station['Latitude']) or pd.isna(station['Longitude']):
                    continue
                
                popup_content = f"""
                    <div style='width: 200px'>
                        <h6 style='margin:0;'>{station['Station Name']}</h6>
                        <hr style='margin:4px 0;'>
                        <p style='margin:0;'>{station['Street Address']}</p>
                        <p style='margin:0;'>{station['City']}, {station['State']}</p>
                        <b>Total Chargers:</b> {int(station['Total_Chargers'])}
                    </div>
                """
                
                folium.Marker(
                    location=[station['Latitude'], station['Longitude']],
                    popup=folium.Popup(popup_content, max_width=300),
                    icon=folium.Icon(color='green', icon='plug', prefix='fa')
                ).add_to(m)
        
        # Save map
        if not os.path.exists('static'):
            os.makedirs('static')
        m.save('static/map.html')
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Helper to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/process', methods=['POST'])
def process():
    csv_file = request.files.get('csv_file')
    graph_type = request.form.get('graph_type')
    if not csv_file:
        return jsonify({'error': 'Please upload a CSV file.'})
    try:
        import io
        station_df = pd.read_csv(io.BytesIO(csv_file.read()), encoding="latin1")
    except Exception as e:
        return jsonify({'error': f'Could not read uploaded file: {e}'})

    # Calculate total chargers for badge update (optional, could be sent back in response)
    total_chargers = int(station_df['Total_Chargers'].sum()) if 'Total_Chargers' in station_df.columns else 0

    # Generate chart based on selection
    chart_filename = f'chart_{uuid.uuid4().hex}.png'
    chart_filepath = os.path.join('static', chart_filename)
    plt.clf()
    try:
        if graph_type == 'correlation_heatmap':
            # Select only numeric columns
            numeric_cols = station_df.select_dtypes(include=['float64', 'int64']).columns
            plt.figure(figsize=(10, 8))
            sns.heatmap(station_df[numeric_cols].corr(), annot=True, cmap="coolwarm")
            plt.title("Correlation Matrix of Numeric Features")
            plt.tight_layout()
            plt.savefig(chart_filepath)
        elif graph_type == 'kmeans_clustering':
            from sklearn.cluster import KMeans
            # Select the proper fields
            df_charger_config = station_df[['Total_Chargers', 'DC_Fast_Chargers', 'EV_Registrations', 'State']].dropna()
            
            # Apply K-Means clustering
            kmeans = KMeans(n_clusters=3, random_state=42)
            df_charger_config['Cluster'] = kmeans.fit_predict(df_charger_config[['Total_Chargers', 'DC_Fast_Chargers']])
            
            # Calculate total EV registrations per cluster (Drop repeating states in dataset)
            df_unique_states = df_charger_config.drop_duplicates(subset='State')
            ev_totals = df_unique_states.groupby('Cluster')['EV_Registrations'].sum().round(0).astype(int)
            
            # Calculate the number of stations per cluster
            station_counts = df_charger_config['Cluster'].value_counts().sort_index()
            
            # Create summary text
            summary_lines = [
                f"Cluster {i}: {station_counts[i]} stations, {ev_totals[i]} EVs"
                for i in sorted(df_charger_config['Cluster'].unique())
            ]
            summary_text = '\n'.join(summary_lines)
            
            # Plot the data
            plt.figure(figsize=(9, 7))
            plt.scatter(
                df_charger_config['Total_Chargers'],
                df_charger_config['DC_Fast_Chargers'],
                c=df_charger_config['Cluster'],
                cmap='viridis',
                s=20
            )
            plt.title('K-Means Clustering of EV Charging Stations')
            plt.xlabel('Total Chargers')
            plt.ylabel('DC Fast Chargers')
            plt.colorbar(label='Cluster ID')
            
            # Add text box to show number of EVs and charging stations per cluster
            plt.gcf().text(
                0.63, 0.73,
                'Cluster Data:\n' + summary_text,
                bbox=dict(facecolor='white', alpha=0.85, edgecolor='black'),
                fontsize=10
            )
            
            plt.tight_layout()
            plt.savefig(chart_filepath)
        elif graph_type == 'dbscan_clustering':
            from sklearn.preprocessing import StandardScaler
            from sklearn.cluster import DBSCAN
            features = ['Level2_Chargers', 'DC_Fast_Chargers']
            df = station_df[features].dropna()
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(df)
            dbscan = DBSCAN(eps=0.5, min_samples=5)
            labels = dbscan.fit_predict(X_scaled)
            plt.figure(figsize=(8, 6))
            plt.scatter(df['Level2_Chargers'], df['DC_Fast_Chargers'], c=labels, cmap='tab10', s=5)
            plt.title("DBSCAN Clustering of Charger Configurations")
            plt.xlabel("Level 2 Chargers")
            plt.ylabel("DC Fast Chargers")
            plt.colorbar(label="Cluster ID")
            plt.tight_layout()
            plt.savefig(chart_filepath)
        elif graph_type == 'birch_clustering':
            from sklearn.preprocessing import StandardScaler
            from sklearn.cluster import Birch
            features = ['Level2_Chargers', 'DC_Fast_Chargers']
            df = station_df[features].dropna()
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(df)
            birch = Birch(n_clusters=5)
            labels = birch.fit_predict(X_scaled)
            plt.figure(figsize=(8, 6))
            plt.scatter(df['Level2_Chargers'], df['DC_Fast_Chargers'], c=labels, cmap='viridis', s=5)
            plt.title("BIRCH Clustering of Charger Configurations")
            plt.xlabel("Level 2 Chargers")
            plt.ylabel("DC Fast Chargers")
            plt.colorbar(label="Cluster ID")
            plt.tight_layout()
            plt.savefig(chart_filepath)
        elif graph_type == 'pie_top5_stations':
            station_counts = station_df.groupby('State')['Total_Chargers'].sum().sort_values(ascending=False)
            plt.figure(figsize=(12, 8))
            plt.pie(station_counts.head(5), labels=station_counts.head(5).index, autopct='%1.1f%%',
                    colors=plt.cm.viridis(np.linspace(0.2, 0.8, 5)), startangle=90)
            plt.title('Top 5 States by Charging Stations (February 2024 Data)', fontsize=14, pad=20)
            plt.savefig(chart_filepath)
        elif graph_type == 'station_distribution':
            return jsonify({'error': 'This graph type is not supported.'})
        else:
            return jsonify({'error': 'Invalid graph type selected.'})
        chart_url = f'/static/{chart_filename}'
        return jsonify({'chart_url': chart_url, 'total_chargers': total_chargers})
    except Exception as e:
        return jsonify({'error': f'Error generating chart: {e}'})

if __name__ == '__main__':
    app.run(debug=True, port=5001) 