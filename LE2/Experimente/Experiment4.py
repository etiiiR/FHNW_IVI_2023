import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objs as go

# Daten laden (Beispiel: Iris-Dataset)
df = pd.read_csv('https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv')

# Schritt 1: Übersicht (Overview)
fig_overview = px.scatter(df, x='sepal_length', y='sepal_width', color='species')
fig_overview.update_layout(title='Übersicht: Sepal Länge vs. Breite')

# Schritt 2: Zoomen und Filtern (Zoom and Filter)
# Hier konzentrieren wir uns auf eine Art, z.B. Setosa
df_filtered = df[df['species'] == 'setosa']
fig_zoom = px.scatter(df_filtered, x='sepal_length', y='sepal_width')
fig_zoom.update_layout(title='Zoom: Setosa Sepal Länge vs. Breite')

# Schritt 3: Details auf Anfrage (Details on Demand)
# Beim Klicken auf einen Punkt zeigen wir detaillierte Informationen an
def create_details_figure(selected_data):
    if selected_data is None:
        return go.Figure()
    
    details = df.iloc[selected_data['pointIndex']]
    fig_details = go.Figure(data=[go.Bar(x=details.index, y=details.values)])
    fig_details.update_layout(title='Details: Eigenschaften des ausgewählten Punktes')
    return fig_details

# Interaktive Elemente hinzufügen (hier simuliert)
selected_point_data = {'pointIndex': 10}  # Simuliert die Auswahl eines Punktes
fig_details = create_details_figure(selected_point_data)

# Kombiniertes Dashboard
fig = make_subplots(rows=3, cols=1, subplot_titles=('Übersicht', 'Zoom', 'Details'))
for trace in fig_overview.data:
    fig.add_trace(trace, row=1, col=1)
for trace in fig_zoom.data:
    fig.add_trace(trace, row=2, col=1)
for trace in fig_details.data:
    fig.add_trace(trace, row=3, col=1)

fig.show()
