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

# %% [markdown]
# ### Install (Conda required)
# conda create -n coiled-datashader -c conda-forge python=3.10 coiled dask s3fs pyarrow datashader hvplot jupyter_bokeh
#
# %conda activate coiled-datashader

# %%
# %pip install coiled dask s3fs pyarrow datashader hvplot jupyter_bokeh --user

# %%
# Read in one year of NYC Taxi data
import dask.dataframe as dd

df = dd.read_parquet(
    "s3://coiled-datasets/dask-book/nyc-tlc/2009",
    storage_options={"anon": True},
)
df.head()

# %%
len(df)

# %%
# %%time

df.sample(frac=0.001).compute().plot(
    x="pickup_longitude", 
    y="pickup_latitude", 
    kind="scatter",
)

# %%
import datashader
from datashader import transfer_functions as tf
from datashader.colors import Hot
import holoviews as hv



def render(df, x_range=(-74.1, -73.7), y_range=(40.6, 40.9)):
    # Plot
    canvas = datashader.Canvas(
        x_range=x_range,
        y_range=y_range,
    )
    agg = canvas.points(
        source=df, 
        x="dropoff_longitude", 
        y="dropoff_latitude", 
        agg=datashader.count("passenger_count"),
    )
    return datashader.transfer_functions.shade(agg, cmap=Hot, how="eq_hist")

# %%time
render(df)


# %%
# load dataset into cluster memory
df.persist()

# %%
# %%time
render(df)

# %%
import hvplot.dask
 
def interact(df):
    return df.hvplot.scatter(
        x="dropoff_longitude", 
        y="dropoff_latitude", 
        aggregator=datashader.count("passenger_count"), 
        datashade=True, cnorm="eq_hist", cmap=Hot,
        width=600, 
        height=400,
    )
 
interact(df)
