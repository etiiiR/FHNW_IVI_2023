import pandas as pd
import plotly.graph_objects as go
import dash
from dash import dcc, html, Input, Output
from faker import Faker
import numpy as np
import random

mapbox_access_token = 'pk.eyJ1IjoiZXRpaWlyIiwiYSI6ImNscW1pdThvYjJyZmoyanJxMWN4YThraTgifQ.LhXan_hQzS2_isDr3jVLkQ'

# get the folder path of the current file
import os
folder_path = os.path.dirname(os.path.realpath(__file__))



# Daten laden
uber_df = pd.read_csv(folder_path + "\\data\\uber.csv")

# Dash-App erstellen
app = dash.Dash(__name__)



faker = Faker()

def generate_synthetic_uber_data(num_rows):
    """
    Generate synthetic Uber data similar to the provided dataset structure.

    Args:
    num_rows (int): Number of rows of synthetic data to generate

    Returns:
    pd.DataFrame: A DataFrame containing the synthetic data
    """

    synthetic_data = []

    for _ in range(num_rows):
        uber_type = random.choice([0, 1, 2])  # Assuming Uber type can be 0, 1, or 2
        origin_region = random.randint(1, 9)  # Assuming regions are numbered 1 to 9
        destination_region = random.randint(1, 9)

        # Generate random coordinates (latitude and longitude)
        origin_latitude = -37.5 + random.random() * 2  # Melbourne latitude range approximation
        origin_longitude = 144.5 + random.random() * 2  # Melbourne longitude range approximation
        destination_latitude = -37.5 + random.random() * 2
        destination_longitude = 144.5 + random.random() * 2

        journey_distance = random.uniform(1000, 50000)  # Random journey distance in meters
        # Generate random dates and convert them to string format
        departure_date = faker.date_between(start_date='-2y', end_date='today').strftime('%Y-%m-%d')
        departure_time = faker.time()

        # Estimating travel time based on distance (simple approximation)
        travel_time = journey_distance / 15.0  # Assuming average speed of 15 m/s
        arrival_time = pd.Timestamp(f'{departure_date} {departure_time}') + pd.Timedelta(seconds=travel_time)
        arrival_time = arrival_time.time()
    
        fare = round(random.uniform(10, 200), 2)  # Random fare in dollars

        synthetic_data.append([
            uber_type, origin_region, destination_region,
            origin_latitude, origin_longitude, destination_latitude, destination_longitude,
            journey_distance, departure_date, departure_time, travel_time,
            arrival_time, fare
        ])

    columns = ['Uber Type', 'Origin Region', 'Destination Region',
               'Origin Latitude', 'Origin Longitude', 'Destination Latitude', 'Destination Longitude',
               'Journey Distance(m)', 'Departure Date', 'Departure Time', 'Travel Time(s)',
               'Arrival Time', 'Fare$']

    return pd.DataFrame(synthetic_data, columns=columns)

# Daten generieren
#uber_df = generate_synthetic_uber_data(1000)

# Layout der App
app.layout = html.Div([
    html.H1("Uber Fahrten Dashboard in Melbourne", style={'textAlign': 'center', 'font-size': '30px', 'font-weight': 'bold', 'font-family': 'Roboto', 'margin-bottom': '30px'}),

    html.Div([
        html.Label("Wählen Sie den Uber Type", style={'font-family': 'Roboto', 'font-weight': 'bold'}),
        dcc.Dropdown(
            id='uber-type-dropdown',
            options=[{'label': 'Alle', 'value': 'Alle'}] + [{'label': str(i), 'value': i} for i in uber_df['Uber Type'].unique()],
            value='Alle'
        ),

        html.Label("Wählen Sie den Fahrpreisbereich:", style={'font-family': 'Roboto', 'font-weight': 'bold', 'margin-top': '20px'}),
        dcc.RangeSlider(
            id='fare-range-slider',
            min=uber_df['Fare$'].min(),
            max=uber_df['Fare$'].max(),
            step=100,
            marks={i: f'${i}' for i in range(int(uber_df['Fare$'].min()), int(uber_df['Fare$'].max()) + 1, 100)},
            value=[uber_df['Fare$'].min(), uber_df['Fare$'].max()]
        ),

        html.Label("Wählen Sie den Entfernungsbereich:", style={'font-family': 'Roboto', 'font-weight': 'bold', 'margin-top': '20px'}),
        dcc.RangeSlider(
            id='distance-range-slider',
            min=uber_df['Journey Distance(m)'].min(),
            max=uber_df['Journey Distance(m)'].max(),
            step=1,
            marks={i: f'{i}m' for i in range(0, int(uber_df['Journey Distance(m)'].max()) + 1, 5000)},
            value=[uber_df['Journey Distance(m)'].min(), uber_df['Journey Distance(m)'].max()]
        ),

        dcc.DatePickerRange(
            id='departure-date-picker',
            min_date_allowed=uber_df['Departure Date'].min(),
            max_date_allowed=uber_df['Departure Date'].max(),
            start_date=uber_df['Departure Date'].min(),
            end_date=uber_df['Departure Date'].max(),
            display_format='DD.MM.YYYY',
            style={'margin-top': '20px'}
        ),
    ], style={'padding': '20px', 'border-radius': '15px', 'box-shadow': '0 4px 8px 0 rgba(0,0,0,0.2)', 'background-color': '#ffffff', 'margin-bottom': '20px'}),

    dcc.Graph(id='map-plot', style={'height': '70vh'}),
], style={'font-family': 'Roboto', 'margin': '40px'})

# Hinzufügen von Hover-Informationen für Details auf Anforderung
def create_hover_info(row):
    return f"Uber Type: {row['Uber Type']}, Fare: ${row['Fare$']}, Distance: {row['Journey Distance(m)']}m"


# Callback für Interaktivität mit mehreren Inputs
@app.callback(
    Output('map-plot', 'figure'),
    [
        Input('uber-type-dropdown', 'value'),
        Input('departure-date-picker', 'start_date'),
        Input('departure-date-picker', 'end_date'),
        Input('fare-range-slider', 'value'),
        Input('distance-range-slider', 'value'),
        # Weitere Inputs für andere Filter
    ]
)
def update_graph(uber_type, start_date, end_date,fare_range, distance_range):
    # Daten filtern
    filtered_df = uber_df if uber_type == 'Alle' else uber_df[uber_df['Uber Type'] == uber_type]

    # Filtern nach Fare$ und Journey Distance
    filtered_df = filtered_df[
        (filtered_df['Fare$'] >= fare_range[0]) &
        (filtered_df['Fare$'] <= fare_range[1]) &
        (filtered_df['Journey Distance(m)'] >= distance_range[0]) &
        (filtered_df['Journey Distance(m)'] <= distance_range[1])
    ]

    if start_date is not None and end_date is not None:
        filtered_df = filtered_df[
            (filtered_df['Departure Date'] >= start_date) &
            (filtered_df['Departure Date'] <= end_date)
        ]
    # Karte erstellen
    fig = go.Figure()

    # Jede Fahrt auf der Karte darstellen mit Hover-Informationen
    for index, row in filtered_df.iterrows():
        hover_info = create_hover_info(row)
        fig.add_trace(go.Scattermapbox(
            lon = [row['Origin Longitude'], row['Destination Longitude']],
            lat = [row['Origin Latitude'], row['Destination Latitude']],
            mode = 'lines+markers',
            marker = dict(size = 10, color = 'red'),
            line = dict(width = 2, color = 'blue'),
            hoverinfo = 'text',
            text = hover_info,
        ))

    # Kartenansicht konfigurieren
    fig.update_layout(
        mapbox = dict(
            accesstoken = mapbox_access_token,
            style = 'mapbox://styles/mapbox/streets-v11',
            center = go.layout.mapbox.Center(lat=-37.8136, lon=144.9631),  # Zentrierung auf Melbourne
            zoom = 9
        ),
        showlegend = True
    )

    return fig

# App ausführen
if __name__ == '__main__':
    app.run_server(debug=False)
