import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
from faker import Faker
import os
import random

mapbox_access_token = "pk.eyJ1IjoiZXRpaWlyIiwiYSI6ImNscW1pdThvYjJyZmoyanJxMWN4YThraTgifQ.LhXan_hQzS2_isDr3jVLkQ"

folder_path = os.path.dirname(os.path.realpath(__file__))
uber_df = pd.read_csv(folder_path + "\\data\\uber.csv").head(50)
synthetic_car_df = pd.read_csv(folder_path + "\\data\\synthetic_car_data.csv")

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

detail_modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Detailansicht"), close_button=True),
        dbc.ModalBody(id="modal-body-content"),
        dbc.ModalFooter(dbc.Button("Schließen", id="close-modal", className="ml-auto")),
    ],
    id="detail-modal",
    is_open=False,
    size="xl",
)


# Erstellen von Dunkelmodus-Plotly-Figuren
def dark_mode_figure(df, x, y, color, title):
    fig = px.scatter(df, x=x, y=y, color=color, title=title)
    fig.update_layout(template="plotly_dark")
    return fig

def dark_mode_histogram(df, x, title ):
    fig = px.histogram(df, x=x, title=title)
    fig.update_layout(template="plotly_dark")
    return fig


sidebar = html.Div(
    [
        html.H2("Filter", style={"textAlign": "center"}),
        dcc.Dropdown(
            id="uber-type-dropdown",
            options=[{"label": "Alle", "value": "Alle"}]
            + [{"label": str(i), "value": i} for i in uber_df["Uber Type"].unique()],
            value="Alle",
            style={"margin-bottom": "20px", "transform": "scale(1.0), z-index: 1000"},
        ),
        dcc.RangeSlider(
            id="fare-range-slider",
            min=uber_df["Fare$"].min(),
            max=uber_df["Fare$"].max(),
            step=100,
            marks={
                i: f"${i}"
                for i in range(
                    int(uber_df["Fare$"].min()), int(uber_df["Fare$"].max()) + 1, 300
                )
            },
            value=[uber_df["Fare$"].min(), uber_df["Fare$"].max()],
        ),
        dcc.RangeSlider(
            id="distance-range-slider",
            min=uber_df["Journey Distance(m)"].min(),
            max=uber_df["Journey Distance(m)"].max(),
            step=1,
            marks={
                i: f"{i}m"
                for i in range(0, int(uber_df["Journey Distance(m)"].max()) + 1, 10000)
            },
            value=[
                uber_df["Journey Distance(m)"].min(),
                uber_df["Journey Distance(m)"].max(),
            ],
        ),
        dcc.DatePickerRange(
            id="departure-date-picker",
            min_date_allowed=uber_df["Departure Date"].min(),
            start_date=uber_df["Departure Date"].min(),
            end_date=uber_df["Departure Date"].max(),
            display_format="DD.MM.YYYY",
            style={
                "margin-top": "20px",
                "transform": "scale(1.0)",
                "transform-origin": "left center",
                "width": "100%",
            },
        ),
        html.Label("Bewertung", style={"font-weight": "bold", "margin-top": "10px"}),
            dcc.Dropdown(
                id="rating-dropdown",
                options=[{"label": str(i), "value": i} for i in range(1, 6, 1)],
                value=None,  # Standardwert ist keine Auswahl
                multi=True,  # Ermöglicht die Auswahl mehrerer Optionen
                placeholder="Wählen Sie Bewertungen",
            ),
    ],
    style={"grid-area": "sidebar", "padding": "10px", "color": "white"},
)

main_content = html.Div(
    [
        html.H1(
            "Deine Uber Fahrten",
            style={"textAlign": "center", "font-size": "30px", "font-weight": "bold", 'padding-top': "20px", 'padding-bottom': "20px"},
        ),
        dcc.Graph(id="map-plot", style={"height": "60vh", 'border-radius': '30px'} ),
        html.Div(
            [
                dcc.Graph(
                    id="fare_histogram",
                    figure=dark_mode_histogram(
                        uber_df, x="Fare$", title="Verteilung der Fahrpreise"
                    ),
                ),
                dcc.Graph(
                    id="distance_scatter",
                    figure=dark_mode_figure(
                        uber_df,
                        "Fare$",
                        "Journey Distance(m)",
                        "Uber Type",
                        "Fahrpreis vs. Reiseentfernung",
                    ),
                ),
            ],
            style={
                "display": "grid",
                "grid-template-columns": "1fr 1fr",
                "grid-gap": "20px",
            },
        ),
        detail_modal,
    ],
    style={"grid-area": "main", "color": "white"},
)

app.layout = html.Div(
    [sidebar, main_content],
    style={
        "display": "grid",
        "grid-template-areas": '"sidebar main"',
        "grid-template-columns": "310px 2fr",
        "height": "100vh",
        "background-color": "#343a40",
    },
)


# Callback zur Aktualisierung der Uber-Typ-Optionen basierend auf der Bewertung
@app.callback(
    Output('uber-type-dropdown', 'options'),
    [Input('rating-dropdown', 'value')],
    [State('uber-type-dropdown', 'value')]
)
def update_uber_type_options(selected_ratings, current_uber_type):
    if selected_ratings:
        # Filtern der Daten basierend auf den ausgewählten Bewertungen
        filtered_df = uber_df[uber_df['Rating'].isin(selected_ratings)]
        # Aktualisieren der Optionen basierend auf den verfügbaren Uber-Typen im gefilterten DataFrame
        options = [{'label': str(i), 'value': i} for i in filtered_df['Uber Type'].unique()]
    else:
        # Standardoptionen, wenn keine Bewertungen ausgewählt sind
        options = [{'label': str(i), 'value': i} for i in uber_df['Uber Type'].unique()]

    # Stellen Sie sicher, dass der aktuelle Wert des Uber-Typ-Dropdowns in den Optionen enthalten ist
    if current_uber_type not in [option['value'] for option in options]:
        current_uber_type = 'Alle'

    return [{'label': 'Alle', 'value': 'Alle'}] + options

# Callback zur Aktualisierung der Fare$ RangeSlider-Optionen basierend auf der Bewertung
@app.callback(
    [Output('fare-range-slider', 'min'),
     Output('fare-range-slider', 'max'),
     Output('fare-range-slider', 'marks'),
     Output('fare-range-slider', 'value')],
    [Input('rating-dropdown', 'value')]
)
def update_fare_range_options(selected_ratings):
    if selected_ratings:
        filtered_df = uber_df[uber_df['Rating'].isin(selected_ratings)]
        min_fare = filtered_df['Fare$'].min()
        max_fare = filtered_df['Fare$'].max()
        marks = {i: f'${i}' for i in range(int(min_fare), int(max_fare) + 1, 300)}
        value = [min_fare, max_fare]
    else:
        min_fare = uber_df['Fare$'].min()
        max_fare = uber_df['Fare$'].max()
        marks = {i: f'${i}' for i in range(int(min_fare), int(max_fare) + 1, 300)}
        value = [min_fare, max_fare]

    return min_fare, max_fare, marks, value


# Callback zur Aktualisierung der Distance RangeSlider-Optionen basierend auf der Bewertung
@app.callback(
    [Output('distance-range-slider', 'min'),
     Output('distance-range-slider', 'max'),
     Output('distance-range-slider', 'marks'),
     Output('distance-range-slider', 'value')],
    [Input('rating-dropdown', 'value')]
)
def update_distance_range_options(selected_ratings):
    if selected_ratings:
        filtered_df = uber_df[uber_df['Rating'].isin(selected_ratings)]
        min_distance = filtered_df['Journey Distance(m)'].min()
        max_distance = filtered_df['Journey Distance(m)'].max()
        marks = {i: f'{i}m' for i in range(0, int(max_distance) + 1, 10000)}
        value = [min_distance, max_distance]
    else:
        min_distance = uber_df['Journey Distance(m)'].min()
        max_distance = uber_df['Journey Distance(m)'].max()
        marks = {i: f'{i}m' for i in range(0, int(max_distance) + 1, 10000)}
        value = [min_distance, max_distance]

    return min_distance, max_distance, marks, value


@app.callback(
    [Output("detail-modal", "is_open"), Output("modal-body-content", "children")],
    [Input("map-plot", "clickData"), Input("close-modal", "n_clicks")],
    [State("detail-modal", "is_open")],
)
def toggle_modal(clickData, close_clicks, is_open):
    ctx = dash.callback_context

    if not ctx.triggered:
        return is_open, None
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if button_id == "map-plot" and clickData:
        # Identifizieren des Index der ausgewählten Fahrt in uber_df
        clicked_index = clickData["points"][0]["curveNumber"]

        # Überprüfen, ob der Index im Bereich der DataFrame-Größe liegt
        if 0 <= clicked_index < len(synthetic_car_df):
            car_data = synthetic_car_df.iloc[clicked_index]
            selected_car = synthetic_car_df.iloc[clicked_index]

            # Erstellen eines Scatter-Plots mit synthetischen Autodaten
            fig = px.scatter(
                synthetic_car_df,
                x="Geschwindigkeit",
                y="Preis",
                color="Markenname",
                hover_data=["Auto Name", "Alter", "Spritverbrauch"],
                title=f'Details für {car_data["Auto Name"]}',
            )
            # Hervorheben des ausgewählten Autos
            fig.add_trace(
                go.Scatter(
                    x=[selected_car["Geschwindigkeit"]],
                    y=[selected_car["Preis"]],
                    mode="markers+text",
                    marker=dict(color="black", size=14),
                    text="Auto deiner Fahrt",
                    textfont=dict(color="black", size=19, family="Roboto"),
                    textposition="top center",
                    showlegend=False,
                )
            )

            return True, dcc.Graph(figure=fig)

        else:
            return True, "Keine entsprechenden Daten gefunden."

    elif button_id == "close-modal":
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
    [
        Output("map-plot", "figure"),
        Output("fare_histogram", "figure"),
        Output("distance_scatter", "figure")
    ],
    [
        Input("uber-type-dropdown", "value"),
        Input("departure-date-picker", "start_date"),
        Input("departure-date-picker", "end_date"),
        Input("fare-range-slider", "value"),
        Input("distance-range-slider", "value"),
        Input("rating-dropdown", "value"),  # Neue Eingabe für die Bewertung
    ],
)
def update_graph(uber_type, start_date, end_date, fare_range, distance_range, ratings):
    # Daten filtern
    filtered_df = (
        uber_df if uber_type == "Alle" else uber_df[uber_df["Uber Type"] == uber_type]
    )

    # Filtern nach Fare$ und Journey Distance
    filtered_df = filtered_df[
        (filtered_df["Fare$"] >= fare_range[0])
        & (filtered_df["Fare$"] <= fare_range[1])
        & (filtered_df["Journey Distance(m)"] >= distance_range[0])
        & (filtered_df["Journey Distance(m)"] <= distance_range[1])
    ]

    if start_date is not None and end_date is not None:
        filtered_df = filtered_df[
            (filtered_df["Departure Date"] >= start_date)
            & (filtered_df["Departure Date"] <= end_date)
        ]
        
    if ratings:
        filtered_df = filtered_df[filtered_df["Rating"].isin(ratings)]

    # Karte erstellen
    fig = go.Figure()
    
    # Histogramm und Scatter-Plot aktualisieren
    hist_fig = dark_mode_histogram(filtered_df, "Fare$", "Verteilung der Fahrpreise")
    scatter_fig = dark_mode_figure(
        filtered_df,
        "Fare$",
        "Journey Distance(m)",
        "Uber Type",
        "Fahrpreis vs. Reiseentfernung",
    )

    # Jede Fahrt auf der Karte darstellen
    for index, row in filtered_df.iterrows():
        legend_label = f'${row["Fare$"]} - {row["Departure Date"]}'
        # Marker und Linien hinzufügen
        fig.add_trace(
            go.Scattermapbox(
                lon=[row["Origin Longitude"], row["Destination Longitude"]],
                lat=[row["Origin Latitude"], row["Destination Latitude"]],
                mode="lines",
                line=dict(width=2, color="blue"),
                hoverinfo="text",
                text=create_hover_info(row),
                name=legend_label,  # Legendenbeschriftung
            )
        )

        # Größe der Marker basierend auf dem Fahrpreis bestimmen
        origin_marker_size = marker_size_based_on_price(row["Fare$"])
        destination_marker_size = marker_size_based_on_price(row["Fare$"])

        # Hinzufügen des Abfahrtspunkts (Origin) mit dynamischer Größe
        fig.add_trace(
            go.Scattermapbox(
                lon=[row["Origin Longitude"]],
                lat=[row["Origin Latitude"]],
                mode="markers",
                marker=dict(size=origin_marker_size, color="green"),
                hoverinfo="text",
                text=create_hover_info(row),
                name='Ziel',  # Legendenbeschriftung
            )
        )

        # Hinzufügen des Ankunftspunkts (Destination) mit dynamischer Größe
        fig.add_trace(
            go.Scattermapbox(
                lon=[row["Destination Longitude"]],
                lat=[row["Destination Latitude"]],
                mode="markers",
                marker=dict(size=destination_marker_size, color="red"),
                hoverinfo="text",
                text=create_hover_info(row),
                name='Abfahrt',  # Legendenbeschriftung
            )
        )

    # Kartenansicht konfigurieren
    fig.update_layout(
        mapbox=dict(
            accesstoken=mapbox_access_token,
            style="mapbox://styles/mapbox/dark-v11",
            center=go.layout.mapbox.Center(
                lat=-37.8136, lon=144.9631
            ),  # Zentrierung auf Melbourne
            zoom=9,
        ),
        margin=dict(l=0, r=0, t=0, b=0),  # Setzen der Ränder auf 0
        showlegend=True,
    )

    return fig, hist_fig, scatter_fig


if __name__ == "__main__":
    app.run_server(debug=True)
