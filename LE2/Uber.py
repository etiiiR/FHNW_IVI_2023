import pandas as pd
import plotly.graph_objects as go
import dash
from dash import dcc, html, Input, Output
mapbox_access_token = 'pk.eyJ1IjoiZXRpaWlyIiwiYSI6ImNscW1pdThvYjJyZmoyanJxMWN4YThraTgifQ.LhXan_hQzS2_isDr3jVLkQ'

# Daten laden
uber_data_url = "https://raw.githubusercontent.com/sohail-sankanur/Cleaning-Uber-Dataset/master/29996368_dirty_data_solution.csv"
uber_df = pd.read_csv(uber_data_url)

# Dash-App erstellen
app = dash.Dash(__name__)

# Layout der App
app.layout = html.Div([
    html.H1("Uber Fahrten Dashboard in Melbourne", style={'textAlign': 'left', 'color': 'gray', 'font-size': '25px', 'font-weight': 'bold', 'font-family': 'Roboto'}),

    # Dropdown für Uber-Typ

    html.Div("Wählen Sie den Uber Type", style={'textAlign': 'left', 'float': 'left','font-family': 'Roboto'}),
    dcc.Dropdown(
        id='uber-type-dropdown',
        options=[{'label': 'Alle', 'value': 'Alle'}] + [{'label': str(i), 'value': i} for i in uber_df['Uber Type'].unique()],
        value='Alle',  # Standardwert auf "Alle" setzen
    ),

    # RangeSlider für Fare$
    html.Div("Wählen Sie den Fahrpreisbereich:", style={'textAlign': 'left', 'margin-top': '20px', 'font-family': 'Roboto'}),
    dcc.RangeSlider(
        id='fare-range-slider',
        min=uber_df['Fare$'].min(),
        max=uber_df['Fare$'].max(),
        step=100,
        marks={i: f'${i}' for i in range(int(uber_df['Fare$'].min()), int(uber_df['Fare$'].max()) + 1, 100)},  # Labels alle 5 Einheiten
        value=[uber_df['Fare$'].min(), uber_df['Fare$'].max()]
    ),

    # RangeSlider für Journey Distance
    html.Div("Wählen Sie den Entfernungsbereich:", style={'textAlign': 'left', 'margin-top': '0px', 'font-family': 'Roboto'}),
    dcc.RangeSlider(
        id='distance-range-slider',
        min=uber_df['Journey Distance(m)'].min(),
        max=uber_df['Journey Distance(m)'].max(),
        step=1,
        marks={i: f'{i}m' for i in range(0, int(uber_df['Journey Distance(m)'].max()) + 1, 5000)},  # Labels alle 5000 Einheiten
        value=[uber_df['Journey Distance(m)'].min(), uber_df['Journey Distance(m)'].max()]
    ),

    # Weitere Dropdowns für Herkunfts- und Zielregion ...
    dcc.DatePickerRange(
        id='departure-date-picker',
        min_date_allowed=uber_df['Departure Date'].min(),
        max_date_allowed=uber_df['Departure Date'].max(),
        start_date=uber_df['Departure Date'].min(),
        end_date=uber_df['Departure Date'].max(),
        display_format='DD.MM.YYYY',
        style={'margin-top': '20px'}
    ),
    dcc.Graph(id='map-plot', style={'height': '70vh'}),
])

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
