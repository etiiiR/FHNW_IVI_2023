import pandas as pd
import plotly.graph_objects as go
import dash
from dash import dcc, html, Input, Output
import numpy as np
import random

# Mapbox Access Token (ersetzen Sie 'YOUR_MAPBOX_ACCESS_TOKEN' mit Ihrem Token)
mapbox_access_token = 'pk.eyJ1IjoiZXRpaWlyIiwiYSI6ImNscW1pdThvYjJyZmoyanJxMWN4YThraTgifQ.LhXan_hQzS2_isDr3jVLkQ'

# Daten laden
flight_paths_df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/2011_february_aa_flight_paths.csv")
airport_traffic_df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/2011_february_us_airport_traffic.csv")

def generate_synthetic_data(num_records):
    # Liste möglicher Flughafencodes und Städte
    airport_codes = ['ORD', 'ATL', 'LAX', 'DFW', 'JFK', 'CDG', 'AMS', 'DXB', 'HND', 'SIN']
    cities = ['Chicago', 'Atlanta', 'Los Angeles', 'Dallas', 'New York', 'Paris', 'Amsterdam', 'Dubai', 'Tokyo', 'Singapore']
    countries = ['USA', 'USA', 'USA', 'USA', 'USA', 'France', 'Netherlands', 'UAE', 'Japan', 'Singapore']
    airlines = ['AA', 'DL', 'UA', 'SW', 'LH', 'AF', 'BA', 'EK', 'NH', 'SQ']

    # Erstellen von Flight Paths Daten
    flight_paths_data = {
        'start_lat': np.random.uniform(-90, 90, num_records),
        'start_lon': np.random.uniform(-180, 180, num_records),
        'end_lat': np.random.uniform(-90, 90, num_records),
        'end_lon': np.random.uniform(-180, 180, num_records),
        'airline': [random.choice(airlines) for _ in range(num_records)],
        'airport1': [random.choice(airport_codes) for _ in range(num_records)],
        'airport2': [random.choice(airport_codes) for _ in range(num_records)],
        'cnt': np.random.randint(100, 1000, num_records)
    }
    flight_paths_df = pd.DataFrame(flight_paths_data)

    airport_traffic_data = {
        'iata': [random.choice(airport_codes) for _ in range(num_records)],
        'airport': [f'{random.choice(airport_codes)} International' for _ in range(num_records)],
        'city': [random.choice(cities) for _ in range(num_records)],
        'state': [random.choice(['IL', 'GA', 'CA', 'TX', 'NY', 'N/A']) for _ in range(num_records)],
        'country': [random.choice(countries) for _ in range(num_records)],
        'lat': np.random.uniform(-90, 90, num_records),
        'long': np.random.uniform(-180, 180, num_records),
        'cnt': np.random.randint(5000, 30000, num_records)
    }
    airport_traffic_df = pd.DataFrame(airport_traffic_data)

    return flight_paths_df, airport_traffic_df


#print("Einzigartige Fluggesellschaften:", flight_paths_df['airline'].unique())  # Überprüfen der einzigartigen Airlines
# Dash-App erstellen
app = dash.Dash(__name__)

# Layout der App
app.layout = html.Div([
    html.H1("Interaktives Flugverkehr-Dashboard", style={'textAlign': 'center'}),
    html.Div([
        dcc.Dropdown(
            id='airport-dropdown',
            options=[{'label': i, 'value': i} for i in airport_traffic_df['iata'].unique()],
            value='ORD',
            style={'width': '30%', 'display': 'inline-block'}
        ),
        dcc.Dropdown(
            id='airline-dropdown',
            options=[{'label': 'Alle', 'value': 'Alle'}] + [{'label': i, 'value': i} for i in flight_paths_df['airline'].unique()],
            value='Alle',
            style={'width': '30%', 'margin-left': '10px', 'display': 'inline-block'}
        )
    ]),
    dcc.Graph(id='map-plot', style={'height': '90vh'}),
])

# Callback für Interaktivität
@app.callback(
    Output('map-plot', 'figure'),
    [Input('airport-dropdown', 'value'),
     Input('airline-dropdown', 'value')]
)
def update_graph(selected_airport, selected_airline):
    # Daten filtern basierend auf den ausgewählten Optionen
    filtered_df = flight_paths_df[
        (flight_paths_df['airport1'] == selected_airport) |
        (flight_paths_df['airport2'] == selected_airport)]

    if selected_airline != 'Alle':
        filtered_df = filtered_df[filtered_df['airline'] == selected_airline]

    # Karte erstellen mit Mapbox
    fig = go.Figure()

    for _, row in filtered_df.iterrows():
        fig.add_trace(go.Scattermapbox(
            lon=[row['start_lon'], row['end_lon']],
            lat=[row['start_lat'], row['end_lat']],
            mode='lines',
            line=dict(width=2, color='blue'),
        ))

    fig.update_layout(
        mapbox=dict(
            accesstoken=mapbox_access_token,
            style='mapbox://styles/mapbox/streets-v11',
        ),
        showlegend=False
    )

    return fig

# App ausführen
if __name__ == '__main__':
    app.run_server(debug=True)