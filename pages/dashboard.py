# Studienarbeit
# Name: Luca Hahn
# Matrikelnr: 1923199
# Betreuer: Prof. Dr. Christof Hübner
# ------------------------------------------------------------------------------------------------------------------
# Main dashboard page (layout & callbacks)

import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from utils import connect_to_db
import config

dash.register_page(__name__, path="/", title="Dashboard", name="Dashboard")
engine = connect_to_db(config.sql)


# Page layout -------------------------------------------------------------------------------------------------------
# Cards to show current data for selected station -------------------------------------------------------------------
def create_card_with_icon(element_of_weather, color, icon):
    card = dbc.CardGroup([
        dbc.Card(
            dbc.CardBody([
                html.H4("N/A", className="card-title", id=f"card_{element_of_weather}"),
                html.P(element_of_weather, className="card-subtitle"),
            ])
        ),
        dbc.Card(
            html.Div(className=icon, style={"fontSize": 30, "margin": "auto"}),
            color=color,
            inverse=True,
            style={"maxWidth": 50}
        ),
    ], className="mt-2 shadow")
    return card


# Current Data from the selected weather station --------------------------------------------------------------------
part_current_data = dbc.Card([
    html.H5(id="station_name", className="card-title"),
    html.P(id="station_updated", className="card-subtitle"),
    dbc.Row([
        dbc.Col([
            create_card_with_icon("Temperatur", config.colors["temperature"], "bi bi-thermometer-half")
        ], xs=12, sm=6, md=4, lg=4, xl=4, xxl=2),
        dbc.Col([
            create_card_with_icon("Luftfeuchtigkeit", config.colors["humidity"], "bi bi-droplet-half")
        ], xs=12, sm=6, md=4, lg=4, xl=4, xxl=2),
        dbc.Col([
            create_card_with_icon("Luftdruck", config.colors["air pressure"], "bi bi-cloud-download")
        ], xs=12, sm=6, md=4, lg=4, xl=4, xxl=2),
        dbc.Col([
            create_card_with_icon("Wind", config.colors["wind"], "bi bi-wind")
        ], xs=12, sm=6, md=4, lg=4, xl=4, xxl=2),
        dbc.Col([
            create_card_with_icon("Niederschlag", config.colors["rain"], "bi bi-cloud-rain")
        ], xs=12, sm=6, md=4, lg=4, xl=4, xxl=2),
        dbc.Col([
            create_card_with_icon("Signalstärke", config.colors["signal"], "bi bi-reception-4")
        ], xs=12, sm=6, md=4, lg=4, xl=4, xxl=2)
    ])
], color="white", outline=True)

# Map with weather stations -----------------------------------------------------------------------------------------
fig_map = px.scatter_mapbox(
    data_frame=config.stations,
    lat="latitude", lon="longitude",
    hover_name="name", hover_data={"latitude": False, "longitude": False},
    center={"lat": 49.4915, "lon": 8.5055}, zoom=13, height=500,
    mapbox_style="open-street-map",
)
fig_map.update_traces(
    mode="markers",
    text="name",
    marker={"size": 10, "color": "purple"},
    selected_marker_size=30,
    customdata=config.stations["name"]
)
fig_map.update_layout(
    margin={"l": 0, "r": 0, "t": 0, "b": 0},
    clickmode="event+select",
    hovermode="closest",
    hoverdistance=2,
)

part_map = dbc.Row([
    dbc.Col([
        html.H5("Positionen der Wetterstationen auf dem BUGA-Gelände"),
        dcc.Graph(id="map", figure=fig_map, config={"displayModeBar": False})
    ])
])

# Selection of data to plot -----------------------------------------------------------------------------------------
part_select_data = dbc.Row([
    dbc.Col([
        html.H5("Auswahl der dargestellten Wetterelemente"),
        dcc.Dropdown(
            id="dropdown_plot",
            options=[
                {"label": "Temperatur & Luftfeuchtigkeit", "value": "temp_humid"},
                {"label": "Luftdruck", "value": "pressure"},
                {"label": "Windgeschwindigkeit & -richtung", "value": "wind"},
                {"label": "Niederschlag", "value": "rain"}
            ],
            value="temp_humid",
            searchable=False,
            clearable=False,
        )
    ])
])

# Plot to show selected data ----------------------------------------------------------------------------------------
part_plot = dbc.Row([
    dbc.Col([
        dcc.Graph(id="graph", config={
            "displaylogo": False,
            'modeBarButtonsToRemove': ["zoomIn", "zoomOut", "resetScale"]
        })
    ], className="mt-2")
])

# Create the page layout by combining all the parts -----------------------------------------------------------------
layout = dbc.Row([
    dbc.Col([
        part_current_data,
        dbc.Row([
            dbc.Col([
                part_map,
            ], xs=12, sm=12, md=12, lg=5, xl=5, xxl=5, className="my-4"),
            dbc.Col([
                part_select_data,
                part_plot
            ], xs=12, sm=12, md=12, lg=7, xl=7, xxl=7, className="my-4")
        ])
    ]),
    dcc.Store(id="dataframe"),
    dcc.Interval(id="dataframe-update", interval=10 * 1000, n_intervals=0)
])

# End page layout ---------------------------------------------------------------------------------------------------


# Page callbacks ----------------------------------------------------------------------------------------------------
# Update the 'global' dataframe every couple of seconds or whenever a new station has been choosen ------------------
@callback(
    Output("station_name", "children"),
    Output("station_updated", "children"),
    Output("dataframe", "data"),
    Input("dataframe-update", "n_intervals"),
    Input("map", "clickData"))
def update_dataframe(n, station_clicked):
    # Make sure a station is selected when loading the page
    if station_clicked is None:
        station = config.stations["name"].iat[0]
    else:
        # Access the name of the station in the clickData attribute
        station = station_clicked["points"][0]["customdata"]

    # Load data into dataframe from choosen station/period
    with engine.connect() as con:
        df = pd.read_sql_table(station, con=con)
    return [
        f"Aktuelle Werte von: {station}",
        f"zuletzt aktualisiert: {df['datetime'].iat[-1]}",
        df.to_json(date_format="iso", orient="split")
    ]


# Update the current values in the cards whenever new data is available----------------------------------------------
@callback(
    Output("card_Temperatur", "children"),
    Output("card_Luftfeuchtigkeit", "children"),
    Output("card_Luftdruck", "children"),
    Output("card_Wind", "children"),
    Output("card_Niederschlag", "children"),
    Output("card_Signalstärke", "children"),
    Input("dataframe", "data"))
def update_cards(df_json):
    last_row = pd.read_json(df_json, orient="split").iloc[-1]
    return [
        f"{last_row['temperature']}°C",
        f"{last_row['humidity']}%",
        f"1.5bar",  # REPLACE WITH DATA
        f"22km/h N",  # REPLACE WITH DATA
        f"6mm",  # REPLACE WITH DATA
        f"{last_row['rssi']}dBm"
    ]


# Update graph ------------------------------------------------------------------------------------------------------
@callback(
    Output("graph", "figure"),
    Input("dataframe", "data"))
def update_line_chart(df_json):
    # Load data and save daily min, mean and max values in separate dataframe
    df = pd.read_json(df_json, orient="split").set_index("datetime")
    df_daily = pd.DataFrame()
    for column in df.columns[1:-1]:
        df_daily[f"{column}_min"] = df[f"{column}"].resample("D").min()
        df_daily[f"{column}_mean"] = df[f"{column}"].resample("D").mean()
        df_daily[f"{column}_max"] = df[f"{column}"].resample("D").max()
    df_daily.reset_index(inplace=True)
    df.reset_index(inplace=True)

    # Create line chart
    fig1 = make_subplots(specs=[[{"secondary_y": True}]])
    fig1.add_trace(
        go.Scattergl(name="Temperatur", x=df["datetime"], y=df["temperature"],
                     mode="lines", marker_color=config.colors["temperature"],
                     hovertemplate="%{y}°C"),
        secondary_y=False,
    )
    fig1.add_trace(
        go.Scattergl(name="Luftfeuchtigkeit", x=df["datetime"], y=df["humidity"],
                     mode="lines", marker_color=config.colors["humidity"],
                     hovertemplate="%{y}%", hoverlabel={"font_color": "white", "bordercolor": "white"}),
        secondary_y=True,
    )

    fig1.update_xaxes(
        rangeselector_buttons=[
            dict(step="all"),
            dict(count=1, label="1Y", step="year", stepmode="backward"),
            dict(count=1, label="YTD", step="year", stepmode="todate"),
            dict(count=1, label="1M", step="month", stepmode="backward"),
            dict(count=7, label="1W", step="day", stepmode="backward"),
            dict(count=1, label="1D", step="day", stepmode="backward"),
            dict(count=6, label="6H", step="hour", stepmode="backward")
        ]
    )
    fig1.update_yaxes(title_text="Temperatur in °C", secondary_y=False,
                      range=[-10, 40], fixedrange=True)
    fig1.update_yaxes(title_text="Luftfeuchtigkeit in %", secondary_y=True, tickmode="sync",
                      range=[0, 100], fixedrange=True)
    fig1.update_layout(margin={"l": 20, "r": 20, "t": 35, "b": 0}, height=460, legend_orientation="h",
                       hovermode="x", uirevision="foo")

    return fig1

# End page callbacks ------------------------------------------------------------------------------------------------
