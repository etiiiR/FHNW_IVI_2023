import datetime
import pandas as pd
import geopandas as gpd
import movingpandas as mpd
from shapely.geometry import Point
import opendatasets as od
import dash
from dash import dcc, html, Input, Output
import hvplot.pandas
import holoviews as hv
from os.path import exists

# Required for displaying hvplot/holoviews in Dash
hv.extension('bokeh')
renderer = hv.renderer('bokeh')

# Function to download and load data
def get_porto_taxi_data():
    input_file_path = 'taxi-trajectory/train.csv'
    if not exists(input_file_path):
        od.download("https://www.kaggle.com/datasets/crailtap/taxi-trajectory")
    df = pd.read_csv(input_file_path, nrows=200, usecols=['TRIP_ID', 'TAXI_ID', 'TIMESTAMP', 'MISSING_DATA', 'POLYLINE'])
    df.POLYLINE = df.POLYLINE.apply(eval)  # string to list
    return df

# Convert unix time to datetime
def unixtime_to_datetime(unix_time):
    return datetime.datetime.fromtimestamp(unix_time)

# Compute datetime for each point
def compute_datetime(row):
    unix_time = row['TIMESTAMP']
    offset = row['running_number'] * datetime.timedelta(seconds=15)
    return unixtime_to_datetime(unix_time) + offset

# Create a Shapely Point from coordinates
def create_point(xy):
    try: 
        return Point(xy)
    except TypeError:  # when there are nan values in the input data
        return None

# Process data
df = get_porto_taxi_data()
new_df = df.explode('POLYLINE')
new_df['geometry'] = new_df['POLYLINE'].apply(create_point)
new_df['running_number'] = new_df.groupby('TRIP_ID').cumcount()
new_df['datetime'] = new_df.apply(compute_datetime, axis=1)
new_df.drop(columns=['POLYLINE', 'TIMESTAMP', 'running_number'], inplace=True)

# Create TrajectoryCollection
trajs = mpd.TrajectoryCollection(
    gpd.GeoDataFrame(new_df, crs=4326), 
    traj_id_col='TRIP_ID', obj_id_col='TAXI_ID', t='datetime')

# Initialize the Dash app
app = dash.Dash(__name__)

# Layout of the app
app.layout = html.Div([
    html.H1("Taxi Trajectory Dashboard"),
    dcc.Graph(id='trajectory-plot', style={'height': '70vh'}),
    # Add more controls or filters as needed here
])

# Callback for updating the map
@app.callback(
    Output('trajectory-plot', 'figure'),
    []  # Add Input components as needed
)
def update_map():
    plot = trajs.hvplot(title='Kaggle Taxi Trajectory Data', tiles='CartoLight')
    plotly_fig = renderer.get_plot(plot).state
    return plotly_fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
