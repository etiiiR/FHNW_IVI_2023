import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import dcc, html, Input, Output, State, callback_context
from faker import Faker
import numpy as np
import random
import dash_bootstrap_components as dbc

mapbox_access_token = 'pk.eyJ1IjoiZXRpaWlyIiwiYSI6ImNscW1pdThvYjJyZmoyanJxMWN4YThraTgifQ.LhXan_hQzS2_isDr3jVLkQ'

# get the folder path of the current file
import os
folder_path = os.path.dirname(os.path.realpath(__file__))


# Modal-Fenster hinzufügen
detail_modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Detailansicht"), close_button=True),
        dbc.ModalBody(id='modal-body-content'),
        
        dbc.ModalFooter(
            dbc.Button("Schließen", id='close-modal', className='ml-auto')
        )
    ],
    id='detail-modal',
    is_open=False,
)

# Daten laden
uber_df = pd.read_csv(folder_path + "\\data\\uber.csv")
# limit to 10 rows
uber_df = uber_df.head(50)
# read synthetic datasynthetic_car_data.csv
synthetic_car_df= pd.read_csv(folder_path + "\\data\\synthetic_car_data.csv")

# Dash-App erstellen
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])



faker = Faker()

def generate_additional_synthetic_uber_data(num_rows):
    """
    Generate additional synthetic Uber data with points always in Melbourne and avoiding water.

    Args:
    num_rows (int): Number of rows of synthetic data to generate

    Returns:
    pd.DataFrame: A DataFrame containing the synthetic data
    """

    synthetic_data = []

    # Define ranges for land coordinates in Melbourne (approximate)
    lat_range = (-37.85, -37.80)  # Adjust these ranges to avoid water
    long_range = (144.90, 145.00)  # Adjust these ranges to avoid water

    for _ in range(num_rows):
        uber_type = random.choice([0, 1, 2])
        origin_region = random.randint(1, 9)
        destination_region = random.randint(1, 9)

        # Generate coordinates within the specified land ranges
        origin_latitude = random.uniform(*lat_range)
        origin_longitude = random.uniform(*long_range)
        destination_latitude = random.uniform(*lat_range)
        destination_longitude = random.uniform(*long_range)

        journey_distance = random.uniform(1000, 50000)
        departure_date = faker.date_between(start_date='-2y', end_date='today').strftime('%Y-%m-%d')
        departure_time = faker.time()

        travel_time = journey_distance / 15.0
        arrival_time = pd.Timestamp(f'{departure_date} {departure_time}') + pd.Timedelta(seconds=travel_time)
        arrival_time = arrival_time.time()

        fare = round(random.uniform(10, 200), 2)

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

additional_uber_data = generate_additional_synthetic_uber_data(3)
uber_df = pd.concat([uber_df, additional_uber_data], ignore_index=True)


# Daten generieren
#uber_df = generate_synthetic_uber_data(1000)

# Layout der App
app.layout = html.Div([
    html.H1("Deine Uber Fahrten", style={'textAlign': 'center', 'font-size': '30px', 'font-weight': 'bold', 'font-family': 'Roboto', 'margin-bottom': '30px'}),
            html.Div([
                html.Label("Wählen Sie den Uber Type", style={'font-family': 'Roboto', 'font-weight': 'bold'}),
                dcc.Dropdown(
                    id='uber-type-dropdown',
                    options=[{'label': 'Alle', 'value': 'Alle'}] + [{'label': str(i), 'value': i} for i in uber_df['Uber Type'].unique()],
                    value='Alle'
                ),
                
                detail_modal,
                html.Label("Wählen Sie den Fahrpreisbereich:", style={'font-family': 'Roboto', 'font-weight': 'bold', 'margin-top': '20px'}),
                dcc.RangeSlider(
                    id='fare-range-slider',
                    min=uber_df['Fare$'].min(),
                    max=uber_df['Fare$'].max(),
                    step=100,
                    marks={i: f'${i}' for i in range(int(uber_df['Fare$'].min()), int(uber_df['Fare$'].max()) + 1, 100)},
                    value=[uber_df['Fare$'].min(), uber_df['Fare$'].max()],
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
                    start_date=uber_df['Departure Date'].min(),
                    end_date=uber_df['Departure Date'].max(),
                    display_format='DD.MM.YYYY',
                    style={'margin-top': '20px'}
                ),
            ], style={'padding': '20px', 'border-radius': '15px', 'box-shadow': '0 4px 8px 0 rgba(0,0,0,0.2)', 'background-color': '#ffffff', 'margin-bottom': '20px'}),

            dcc.Graph(id='map-plot', style={'height': '70vh'}),
], style={'font-family': 'Roboto', 'margin': '40px'})


@app.callback(
    [Output('detail-modal', 'is_open'), Output('modal-body-content', 'children')],
    [Input('map-plot', 'clickData'), Input('close-modal', 'n_clicks')],
    [State('detail-modal', 'is_open')]
)
def toggle_modal(clickData, close_clicks, is_open):
    ctx = dash.callback_context

    if not ctx.triggered:
        return is_open, None
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'map-plot' and clickData:
        # Identifizieren des Index der ausgewählten Fahrt in uber_df
        clicked_index = clickData['points'][0]['curveNumber']

        # Überprüfen, ob der Index im Bereich der DataFrame-Größe liegt
        if 0 <= clicked_index < len(synthetic_car_df):
            car_data = synthetic_car_df.iloc[clicked_index]
            selected_car = synthetic_car_df.iloc[clicked_index]
            
            # Erstellen eines Scatter-Plots mit synthetischen Autodaten
            fig = px.scatter(
                synthetic_car_df, 
                x='Geschwindigkeit', 
                y='Preis', 
                color='Markenname',
                hover_data=['Auto Name', 'Alter', 'Spritverbrauch'],
                title=f'Details für {car_data["Auto Name"]}'
            )
            # Hervorheben des ausgewählten Autos
            fig.add_trace(go.Scatter(
                x=[selected_car['Geschwindigkeit']],
                y=[selected_car['Preis']],
                mode='markers+text',
                marker=dict(color='black', size=14),
                text='Auto deiner Fahrt',
                textfont=dict(color='black', size=19, family='Roboto'),
                textposition='top center',
                showlegend=False,
            ))

            return True, dcc.Graph(figure=fig)

        else:
            return True, "Keine entsprechenden Daten gefunden."

    elif button_id == 'close-modal':
        return False, None

    return is_open, None


# Hinzufügen von Hover-Informationen für Details auf Anforderung
def create_hover_info(row):
    return f"Uber Type: {row['Uber Type']}, Fare: ${row['Fare$']}, Distance: {row['Journey Distance(m)']}m"


def marker_size_based_on_price(price):
    # Festlegen eines Skalierungsfaktors für die Markergröße
    scale_factor = 0.01  # Passen Sie diesen Faktor an Ihre Daten an
    base_size = 10  # Grundgröße des Markers
    return base_size + price * scale_factor

@app.callback(
    Output('map-plot', 'figure'),
    [
        Input('uber-type-dropdown', 'value'),
        Input('departure-date-picker', 'start_date'),
        Input('departure-date-picker', 'end_date'),
        Input('fare-range-slider', 'value'),
        Input('distance-range-slider', 'value'),
    ]
)
def update_graph(uber_type, start_date, end_date, fare_range, distance_range):
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


    # Jede Fahrt auf der Karte darstellen
    for index, row in filtered_df.iterrows():
        # Marker und Linien hinzufügen
        fig.add_trace(go.Scattermapbox(
            lon=[row['Origin Longitude'], row['Destination Longitude']],
            lat=[row['Origin Latitude'], row['Destination Latitude']],
            mode='lines',
            line=dict(width=2, color='blue'),
            hoverinfo='text',
            text=create_hover_info(row)
        ))

        # Größe der Marker basierend auf dem Fahrpreis bestimmen
        origin_marker_size = marker_size_based_on_price(row['Fare$'])
        destination_marker_size = marker_size_based_on_price(row['Fare$'])

        # Hinzufügen des Abfahrtspunkts (Origin) mit dynamischer Größe
        fig.add_trace(go.Scattermapbox(
            lon=[row['Origin Longitude']],
            lat=[row['Origin Latitude']],
            mode='markers',
            marker=dict(size=origin_marker_size, color='green'),
            hoverinfo='text',
            text=create_hover_info(row)
        ))

        # Hinzufügen des Ankunftspunkts (Destination) mit dynamischer Größe
        fig.add_trace(go.Scattermapbox(
            lon=[row['Destination Longitude']],
            lat=[row['Destination Latitude']],
            mode='markers',
            marker=dict(size=destination_marker_size, color='red'),
            hoverinfo='text',
            text=create_hover_info(row)
        ))


    # Kartenansicht konfigurieren
    fig.update_layout(
        mapbox=dict(
            accesstoken=mapbox_access_token,
            style='mapbox://styles/mapbox/streets-v11',
            center=go.layout.mapbox.Center(lat=-37.8136, lon=144.9631),  # Zentrierung auf Melbourne
            zoom=9
        ),
        showlegend=False
    )

    return fig


# App ausführen
if __name__ == '__main__':
    app.run_server(debug=True)
