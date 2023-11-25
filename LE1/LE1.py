# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.15.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %%
import pandas as pd
import time
import numpy as np
import plotly.express as px
import datashader as ds
from colorcet import fire
import datashader.transfer_functions as tf

# %%
df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/uber-rides-data1.csv')
dff = df.query('Lat < 40.82').query('Lat > 40.70').query('Lon > -74.02').query('Lon < -73.91')

import datashader as ds
cvs = ds.Canvas(plot_width=1000, plot_height=1000)
agg = cvs.points(dff, x='Lon', y='Lat')
# agg is an xarray object, see http://xarray.pydata.org/en/stable/ for more details
coords_lat, coords_lon = agg.coords['Lat'].values, agg.coords['Lon'].values
# Corners of the image, which need to be passed to mapbox
coordinates = [[coords_lon[0], coords_lat[0]],
               [coords_lon[-1], coords_lat[0]],
               [coords_lon[-1], coords_lat[-1]],
               [coords_lon[0], coords_lat[-1]]]

from colorcet import fire
import datashader.transfer_functions as tf
img = tf.shade(agg, cmap=fire)[::-1].to_pil()

import plotly.express as px
# Trick to create rapidly a figure with mapbox axes
fig = px.scatter_mapbox(dff[:1], lat='Lat', lon='Lon', zoom=12)
# Add the datashader image as a mapbox layer image
fig.update_layout(mapbox_style="carto-darkmatter",
                 mapbox_layers = [
                {
                    "sourcetype": "image",
                    "source": img,
                    "coordinates": coordinates
                }]
)
# save the figure as a html file
fig.write_html("uber_nyc.html")

# %%
import pandas as pd
import plotly.express as px

# Load the data
df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/uber-rides-data1.csv')

# Filter the data
dff = df.query('40.70 < Lat < 40.82').query('-74.02 < Lon < -73.91')

# Create a scatter plot on a map
fig = px.scatter_mapbox(dff, lat='Lat', lon='Lon', zoom=10, height=300)

# Update the layout to use a dark map style
fig.update_layout(mapbox_style="carto-darkmatter")

# Show the figure
fig.write_html("uber_nyc.html")


# %%
# Function to simulate filtering data based on a zoom level to mimic LOD
def filter_data(df, zoom_level):
    if zoom_level < 10:
        # At low zoom levels, sample the dataset to reduce size
        frac = 1 / (11 - zoom_level)  # Less detail as we zoom out
        return df.sample(frac=frac)
    else:
        # At high zoom levels, use the full dataset
        return df
    

# Function to simulate the rendering of a subset of the data and measure time
def benchmark_data_size(df, fraction):
    start_time = time.time()
    
    # Reduce the dataset according to the fraction specified
    dff = df.sample(frac=fraction) if fraction < 1 else df
    
    # Visualization code with datashader
    cvs = ds.Canvas(plot_width=500, plot_height=500)
    agg = cvs.points(dff, 'Lon', 'Lat')
    img = tf.shade(agg, cmap=fire)[::-1].to_pil()
    
    end_time = time.time()
    return end_time - start_time  # Return the time taken to simulate rendering

# Function to simulate rendering the visualization and measure time
def benchmark_rendering(df, zoom_level, width=500, height=500):
    start_time = time.time()
    
    # Filter data based on zoom level
    dff = filter_data(df, zoom_level)
    
    # Visualization code
    cvs = ds.Canvas(plot_width=width, plot_height=height)
    agg = cvs.points(dff, 'Lon', 'Lat')
    img = tf.shade(agg, cmap=fire)[::-1].to_pil()

    # Using Plotly to display the data - not the actual rendering time
    fig = px.scatter_mapbox(dff[:1], lat='Lat', lon='Lon', zoom=zoom_level)
    fig.update_layout(mapbox_style="carto-darkmatter",
                      mapbox_layers=[{
                          "sourcetype": "image",
                          "source": img,
                          "coordinates": [[-74.02, 40.70], [-73.91, 40.70], [-73.91, 40.82], [-74.02, 40.82]]
                      }]
                     )
    # Note: This will not display in a non-interactive environment
# fig.show()

    end_time = time.time()
    return end_time - start_time  # Return the time taken to simulate rendering







# %%
# Benchmark performance at different zoom levels
zoom_levels = [5, 8, 10, 12, 15]
for zoom in zoom_levels:
    time_taken = benchmark_rendering(df, zoom)
    print(f"Time taken to render at zoom level {zoom}: {time_taken:.4f} seconds")

# %%
# Benchmark performance at different zoom levels
zoom_levels = [5, 8, 10, 12, 15]
for zoom in zoom_levels:
    time_taken = benchmark_rendering(df, zoom, width=10000, height=10000)
    print(f"Time taken to render at zoom level {zoom}: {time_taken:.4f} seconds")


# %%
def benchmark_plotly_rendering(df, zoom, width=500, height=500):
    start_time = time.time()
    
    # Create Plotly figure using native scatter
    fig = px.scatter_mapbox(df, lat='Lat', lon='Lon', zoom=zoom, height=height, width=width)
    fig.update_layout(mapbox_style="carto-darkmatter")
    fig.update_traces(marker=dict(size=3))
    
    # We don't actually display the figure in this benchmarking function.
    # In a live environment, you would use fig.show()
    
    end_time = time.time()
    return end_time - start_time  # Return the time taken for this rendering approach

# Benchmark performance at different zoom levels
zoom_levels = [5, 8, 10, 12, 15]
for zoom in zoom_levels:
    time_taken = benchmark_plotly_rendering(df, zoom)
    print(f"Time taken to render at zoom level {zoom} with Plotly native scatter: {time_taken:.4f} seconds")

# %%
# Data size benchmarks
fractions = [0.01, 0.05, 0.1, 0.5, 1]  # Fractions of the original data size to use in the benchmark
for fraction in fractions:
    time_taken = benchmark_data_size(df, fraction)
    data_size = len(df) * fraction
    print(f"Time taken to render with {data_size:.0f} data points (fraction: {fraction}): {time_taken:.4f} seconds")

# %%
# Benchmark rendering with actual larger datasets by duplicating the dataframe
multiples = [1, 2, 5, 10, 100, 1000]  # Multiples of the original data size
for multiple in multiples:
    # Concatenate the dataframe to itself 'multiple' times
    larger_df = pd.concat([df] * multiple)
    time_taken = benchmark_data_size(larger_df, 1)
    data_size = len(larger_df)
    print(f"Time taken to render with {data_size} data points (multiple: {multiple}): {time_taken:.4f} seconds")
    # plot the time taken to render with data size
import matplotlib.pyplot as plt
plt.plot([len(df) * multiple for multiple in multiples], [benchmark_data_size(pd.concat([df] * multiple), 1) for multiple in multiples])
plt.xlabel('Data size')
plt.ylabel('Time (seconds)')
plt.title('Datashader rendering time vs data size')
plt.show()


# %%
import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt
import datashader as ds
import datashader.transfer_functions as tf

# Load the dataset
df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/uber-rides-data1.csv')

# Define the rendering functions for comparison
def render_matplotlib(df):
    plt.scatter(df['Lon'], df['Lat'], s=1, alpha=0.1)
    plt.show()

def render_datashader(df):
    cvs = ds.Canvas(plot_width=500, plot_height=500)
    agg = cvs.points(df, 'Lon', 'Lat')
    img = tf.shade(agg, cmap=['lightblue', 'darkblue'])
    img.to_pil().show()

# Benchmarking function
def benchmark_rendering(df, rendering_function):
    start_time = time.time()
    rendering_function(df)
    end_time = time.time()
    return end_time - start_time

# Perform benchmarking
matplotlib_time = benchmark_rendering(df, render_matplotlib)
datashader_time = benchmark_rendering(df, render_datashader)

print(f"Matplotlib rendering time: {matplotlib_time:.4f} seconds")
print(f"Datashader rendering time: {datashader_time:.4f} seconds")

## %%
# plot the matplotlib vs datashader rendering times
import matplotlib.pyplot as plt
plt.bar(['Matplotlib', 'Datashader'], [matplotlib_time, datashader_time])
plt.ylabel('Time (seconds)')
plt.title('Matplotlib vs Datashader rendering times')
plt.show()



