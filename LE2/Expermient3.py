import pandas as pd
import plotly.graph_objects as go
import dash
from dash import dcc, html, Input, Output

# Load the datasets
flight_paths_df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/2011_february_aa_flight_paths.csv")
airport_traffic_df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/2011_february_us_airport_traffic.csv")

# Create the Dash app
app = dash.Dash(__name__)

# Layout of the app
app.layout = html.Div([
    html.H1("Interactive Air Traffic Dashboard"),
    dcc.Graph(id='map-plot'),
    html.Div([
        dcc.Dropdown(
            id='airport-dropdown',
            options=[{'label': i, 'value': i} for i in airport_traffic_df['iata'].unique()],
            value='ORD'
        ),
    ], style={'width': '30%', 'display': 'inline-block'})
])

# Callback for interactivity
@app.callback(
    Output('map-plot', 'figure'),
    [Input('airport-dropdown', 'value')]
)
def update_graph(selected_airport):
    # Filter data based on the selected airport
    filtered_df = flight_paths_df[
        (flight_paths_df['airport1'] == selected_airport) | (flight_paths_df['airport2'] == selected_airport)]

    # Create the plot using plotly.graph_objects
    fig = go.Figure()

    for _, row in filtered_df.iterrows():
        fig.add_trace(go.Scattergeo(
            lon = [row['start_lon'], row['end_lon']],
            lat = [row['start_lat'], row['end_lat']],
            mode = 'lines',
            line = dict(width = 2, color = 'blue'),
        ))

    fig.update_layout(
        title_text = f'Flight Paths from/to {selected_airport}',
        showlegend = False,
        geo = dict(
            scope = 'world',
            projection_type = 'equirectangular',
            showland = True,
            landcolor = 'rgb(243, 243, 243)',
            countrycolor = 'rgb(204, 204, 204)',
        ),
    )

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
