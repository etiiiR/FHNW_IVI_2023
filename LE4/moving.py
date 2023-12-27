import datetime
import pandas as pd
import geopandas as gpd
import opendatasets as od
from os.path import exists
from shapely.geometry import Point
import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go

# Function to download the dataset from Kaggle
def get_porto_taxi_from_kaggle():
    dataset_url = "https://www.kaggle.com/datasets/crailtap/taxi-trajectory"
    input_file_path = 'taxi-trajectory/train.csv'
    if not exists(input_file_path):
        od.download(dataset_url, force=True)
    return input_file_path

# Function to process the dataset
def process_taxi_data(input_file_path, nrows):
    df = pd.read_csv(input_file_path, nrows=nrows, usecols=['TRIP_ID', 'TAXI_ID', 'TIMESTAMP', 'POLYLINE'])
    df.POLYLINE = df.POLYLINE.apply(eval)  # Convert string to list

    def unixtime_to_datetime(unix_time):
        return datetime.datetime.fromtimestamp(unix_time)

    def compute_datetime(row):
        unix_time = row['TIMESTAMP']
        offset = row['running_number'] * datetime.timedelta(seconds=15)
        return unixtime_to_datetime(unix_time) + offset

    def create_point(xy):
        return Point(xy) if xy else None

    new_df = df.explode('POLYLINE')
    new_df['geometry'] = new_df['POLYLINE'].apply(create_point)
    new_df['running_number'] = new_df.groupby('TRIP_ID').cumcount()
    new_df['datetime'] = new_df.apply(compute_datetime, axis=1)
    new_df.drop(columns=['POLYLINE', 'TIMESTAMP', 'running_number'], inplace=True)
    gdf = gpd.GeoDataFrame(new_df, crs=4326)

    return gdf

# Dash application setup
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Porto Taxi Trajectory Visualization"),
    dcc.Input(id='nrows-input', type='number', value=200, placeholder='Enter number of rows'),
    html.Button('Submit', id='submit-val', n_clicks=0),
    dcc.Graph(id='map-plot', style={'height': '70vh'})
])

@app.callback(
    Output('map-plot', 'figure'),
    [Input('submit-val', 'n_clicks')],
    [State('nrows-input', 'value')]
)
def update_output(n_clicks, nrows):
    if n_clicks > 0:
        input_file_path = get_porto_taxi_from_kaggle()
        gdf = process_taxi_data(input_file_path, nrows)

        fig = go.Figure()

        # Group data by TRIP_ID and plot each trajectory
        for trip_id, trip_data in gdf.groupby('TRIP_ID'):
            fig.add_trace(go.Scattermapbox(
                lat=trip_data.geometry.y,
                lon=trip_data.geometry.x,
                mode='lines',  # Changed from 'markers' to 'lines'
                line=dict(width=2),
                name=f'Trip {trip_id}'
            ))

        fig.update_layout(
            hovermode='closest',
            mapbox=dict(
                bearing=0,
                center=go.layout.mapbox.Center(lat=gdf.geometry.y.mean(), lon=gdf.geometry.x.mean()),
                pitch=0,
                zoom=10,
                style='open-street-map'
            )
        )

        return fig
    else:
        return go.Figure()

if __name__ == '__main__':
    app.run_server(debug=True)
