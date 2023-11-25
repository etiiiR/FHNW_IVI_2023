from bokeh.plotting import figure, output_file, save
from bokeh.models import ColumnDataSource
from bokeh.io import reset_output
from time import time
import numpy as np
import pandas as pd

# Generate a large dataset
N = 1000000  # Number of points
df = pd.DataFrame({
    'x': np.random.randn(N),
    'y': np.random.randn(N)
})

# Convert DataFrame to ColumnDataSource
source = ColumnDataSource(df)

# Function to create and save a scatter plot without performance tweaks
def save_plot_without_tweaks(source, filename):
    output_file(filename)
    p = figure(title="Scatter plot without tweaks", width=600, height=600, output_backend="canvas")
    p.scatter(x='x', y='y', source=source, size=1, alpha=0.1)
    save(p)
    reset_output()  # Reset output state after saving

# Function to create and save a scatter plot with WebGL acceleration
def save_plot_with_webgl(source, filename):
    output_file(filename)
    p = figure(title="Scatter plot with WebGL", width=600, height=600, output_backend="webgl")
    p.scatter(x='x', y='y', source=source, size=1, alpha=0.1)
    save(p)
    reset_output()  # Reset output state after saving

# Benchmarking function
def benchmark_saving(plot_func, source, filename):
    start_time = time()
    plot_func(source, filename)
    end_time = time()
    return end_time - start_time

# Main block to run benchmarking
if __name__ == "__main__":
    time_without_tweaks = benchmark_saving(save_plot_without_tweaks, source, "scatter_without_tweaks.html")
    time_with_webgl = benchmark_saving(save_plot_with_webgl, source, "scatter_with_webgl.html")

    print("Time without tweaks: {:.2f} seconds".format(time_without_tweaks))
    print("Time with WebGL: {:.2f} seconds".format(time_with_webgl))
    if time_with_webgl > 0:
        print("WebGL is {:.2f} times faster".format(time_without_tweaks / time_with_webgl))
    else:
        print("WebGL time measurement failed, can't compute speedup.")
