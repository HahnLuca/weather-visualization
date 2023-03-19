# Studienarbeit
# Name: Luca Hahn
# Matrikelnr: 1923199
# Betreuer: Prof. Dr. Christof Hübner
# ------------------------------------------------------------------------------------------------------------------
# Main dashboard page (layout & callbacks)

import dash
import numpy as np
from dash import html, dcc, callback, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate
from geopy.distance import great_circle
from plotly.subplots import make_subplots
import pandas as pd
from sqlalchemy import text

from database import engine
from config import table_stations, elements

dash.register_page(__name__, path="/", title="Dashboard", name="Dashboard")

# Page layout -------------------------------------------------------------------------------------------------------
# Current Data from the selected weather station --------------------------------------------------------------------
part_current_data = dbc.Card([
    html.H5(id="station_name", className="card-title"),
    html.P(id="station_updated", className="card-subtitle"),
    dbc.Row([
        # Create a column for every element of weather
        dbc.Col([
            dbc.CardGroup([
                dbc.Card(
                    dbc.CardBody([
                        html.H4("N/A", className="card-title", id=f"card_{element}"),
                        html.P(elements[element]["name"], className="card-subtitle"),
                    ])
                ),
                dbc.Card(
                    html.Div(className=elements[element]["icon"], style={"fontSize": 30, "margin": "auto"}),
                    color=elements[element]["color"], inverse=True, style={"maxWidth": 50}
                ),
            ], className="mt-2 shadow")
        ], xs=12, sm=6, md=4, lg=4, xl=4, xxl=2) for element in elements
    ])
], color="white", outline=True)

# Station selection over dropdown or map ----------------------------------------------------------------------------
part_map = dbc.Row([
    dbc.Col([
        html.H5("Auswahl einer Wetterstation"),
        dcc.Dropdown(id="dropdown_stations", searchable=False, clearable=False),
        dcc.Graph(id="map", config={"displayModeBar": False}, className="mt-2"),
        # Dummy input for map callback, callback is meant to be triggerd mainly on page refreshing
        dcc.Interval(id="map_update", interval=60 * 60 * 1000, n_intervals=0),
        dcc.Store(id="current_station_id")
    ])
])

# Plot for selected data --------------------------------------------------------------------------------------------
part_data = dbc.Row([
    dbc.Col([
        html.H5("Auswahl der dargestellten Wetterelemente"),
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(
                    id="dropdown_element", searchable=False, clearable=False,
                    options=[
                        {"label": f"{elements['temperature']['name']} & {elements['humidity']['name']}",
                         "value": "temperature_humidity"},
                        {"label": f"{elements['windspeed']['name']} & {elements['winddirection']['name']}",
                         "value": "windspeed_winddirection"},
                        {"label": f"{elements['rain']['name']}", "value": "rain"},
                        {"label": f"{elements['rssi']['name']}", "value": "rssi"}
                    ],
                    value="temperature_humidity",
                )
            ], xs=12, sm=12, md=6, lg=12, xl=6, xxl=6),
            dbc.Col([
                dbc.RadioItems(
                    id="radio_sampling", inline=True,
                    options=[
                        {"label": "Alle Messwerte", "value": "all"},
                        {"label": "Nur Tageswerte", "value": "daily"},
                    ],
                    value="all",
                ),
            ], xs=12, sm=12, md=6, lg=12, xl=6, xxl=6)
        ]),
        dcc.Graph(id="graph", config={
            "displaylogo": False,
            "modeBarButtonsToRemove": ["zoomIn", "zoomOut", "resetScale"]
        }, className="mt-2")
    ])
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
                part_data
            ], xs=12, sm=12, md=12, lg=7, xl=7, xxl=7, className="my-4")
        ])
    ]),
    dcc.Store(id="dataframe"),
    dcc.Interval(id="dataframe_update", interval=10 * 1000, n_intervals=0)
])


# End page layout ---------------------------------------------------------------------------------------------------


# Page callbacks ----------------------------------------------------------------------------------------------------
# Update stations in dropdown and map on page refreshing ------------------------------------------------------------
@callback(
    Output("dropdown_stations", "options"),
    Output("map", "figure"),
    Input("map_update", "n_intervals"))
def update_possible_stations(n):
    with engine.connect() as con:
        df_stations = pd.read_sql_table(table_stations, con)
    dropdown_options = [
        {"label": station["Name"], "value": station["ID"]} for index, station in df_stations.iterrows()
    ]

    # Check if any stations are available
    if dropdown_options:
        # Calculate distance between minimal and maximal station coordinates and set minimal distance for zoom
        diff_km = great_circle((df_stations["Breitengrad"].min(), df_stations["Längengrad"].min()),
                               (df_stations["Breitengrad"].max(), df_stations["Längengrad"].max())).km
        diff_km = max(diff_km, 5)
        # Estimate zoom level to fit all points in 350 pixel wide map (map height = 450p, map width varies)
        # https://docs.mapbox.com/help/glossary/zoom-level/
        km_per_pixel_at_zoom_0 = 50  # Valid around latitude = 50°
        zoom = np.log2(km_per_pixel_at_zoom_0 / (diff_km / 350))

        # Create map with selectable stations
        fig_map = px.scatter_mapbox(
            data_frame=df_stations, lat="Breitengrad", lon="Längengrad",
            hover_name="Name", hover_data={"Breitengrad": False, "Längengrad": False},
            center={"lat": (df_stations["Breitengrad"].max() + df_stations["Breitengrad"].min()) / 2,
                    "lon": (df_stations["Längengrad"].max() + df_stations["Längengrad"].min()) / 2},
            zoom=zoom, height=450, mapbox_style="open-street-map",
        )
        fig_map.update_traces(
            mode="markers", marker={"size": 10, "color": "purple"},
            selected_marker={"size": 10, "color": "purple"}, customdata=df_stations["ID"]
        )
        fig_map.update_layout(
            margin={"l": 0, "r": 0, "t": 0, "b": 0}, clickmode="event+select",
            hovermode="closest", hoverdistance=2,
        )
        return dropdown_options, fig_map

    # Abort callback if no station available
    else:
        raise PreventUpdate


# Update current station and dropdown value if selection was made in map --------------------------------------------
@callback(
    Output("current_station_id", "data"),
    Output("dropdown_stations", "value"),
    Input("dropdown_stations", "value"),
    Input("map", "clickData"))
def update_current_station(station_dropdown, station_map):
    # Select station depending on callback trigger
    if "dropdown_stations" == ctx.triggered_id and station_dropdown:
        station_id = station_dropdown
    elif "map" == ctx.triggered_id and station_map:
        station_id = station_map["points"][0]["customdata"]
    # Make sure a station is selected when loading the page
    else:
        with engine.connect() as con:
            station_id = pd.read_sql_table(table_stations, con)
        if not station_id.empty:
            station_id = station_id["ID"].iat[0]
        # Abort callback if no station available
        else:
            raise PreventUpdate
    return station_id, station_id


# Update the 'global' dataframe every couple of seconds or whenever a new station has been choosen ------------------
@callback(
    Output("dataframe", "data"),
    Input("dataframe_update", "n_intervals"),
    Input("current_station_id", "data"),
    Input("radio_sampling", "value"),
    Input("dropdown_element", "value"))
def update_dataframe(n, station_id, sampling, element_types):
    if station_id:
        # Load selected elements into dataframe from choosen station
        with engine.connect() as con:
            df = pd.read_sql_table("station" + str(station_id), index_col="timestamp",
                                   columns=element_types.split("_"), con=con)

        # Dataframe contains all the data from the last month
        if sampling == "all":
            df = df.last("31D")
            df.reset_index(inplace=True)
            return df.to_json(date_format="iso", orient="split")

        # Dataframe contains only certain daily values from alltime
        else:
            df_daily = pd.DataFrame()
            for column in df.columns:
                df_daily[f"{column}_min"] = df[f"{column}"].resample("D").min()
                df_daily[f"{column}_mean"] = df[f"{column}"].resample("D").mean().round(1)
                df_daily[f"{column}_max"] = df[f"{column}"].resample("D").max()
            df_daily.reset_index(inplace=True)
            return df_daily.to_json(date_format="iso", orient="split")
    # Abort callback if no station available
    else:
        raise PreventUpdate


# Update the current values in the cards whenever dataframe got updated ---------------------------------------------
@callback(
    Output("station_name", "children"),
    Output("station_updated", "children"),
    Output("card_temperature", "children"),
    Output("card_humidity", "children"),
    Output("card_windspeed", "children"),
    Output("card_winddirection", "children"),
    Output("card_rain", "children"),
    Output("card_rssi", "children"),
    Input("dataframe", "data"),
    State("current_station_id", "data"))
def update_cards(df_json, station_id):
    # Get station name and last data from corresponding station id
    with engine.connect() as con:
        station_name = pd.read_sql_query(text(f"SELECT Name FROM {table_stations} "
                                              f"WHERE ID = {station_id}"), con)["Name"].iat[0]
        last_row = pd.read_sql_query(text(f"SELECT * FROM station{station_id} ORDER BY ID DESC LIMIT 1"), con)
        last_row.replace(to_replace=[None], value="N/A", inplace=True)

    return [
        f"Aktuelle Werte von: {station_name}",
        f"zuletzt aktualisiert: {last_row['timestamp'].iat[0]}"
    ] + [f"{last_row[element].iat[0]}{elements[element]['unit']}" for element in elements]


# Update graph ------------------------------------------------------------------------------------------------------
@callback(
    Output("graph", "figure"),
    Input("dataframe", "data"),
    State("radio_sampling", "value"),
    State("dropdown_element", "value"))
def update_plot(df_json, sampling, elem_type):
    # Create basic line chart
    fig1 = make_subplots(specs=[[{"secondary_y": True}]])
    fig1.update_layout(margin={"l": 20, "r": 20, "t": 35, "b": 0}, height=450, legend_orientation="h",
                       hovermode="x", uirevision="foo")

    # Configure the rangeselector buttons depending on which sampling level has been choosen
    if sampling == "daily":
        fig1.update_xaxes(
            rangeselector_buttons=[
                dict(count=1, label="1Y", step="year", stepmode="backward"),
                dict(count=6, label="6M", step="month", stepmode="backward"),
                dict(count=3, label="3M", step="month", stepmode="backward"),
                dict(count=1, label="1M", step="month", stepmode="backward"),
                dict(count=14, label="2W", step="day", stepmode="backward"),
                dict(count=7, label="1W", step="day", stepmode="backward")
            ]
        )
    else:
        fig1.update_xaxes(
            rangeselector_buttons=[
                dict(count=1, label="1M", step="month", stepmode="backward"),
                dict(count=14, label="2W", step="day", stepmode="backward"),
                dict(count=7, label="1W", step="day", stepmode="backward"),
                dict(count=3, label="3D", step="day", stepmode="backward"),
                dict(count=1, label="1D", step="day", stepmode="backward"),
                dict(count=12, label="12H", step="hour", stepmode="backward")
            ]
        )

    # Load data and get element types to plot
    df = pd.read_json(df_json, orient="split")
    elem_type = elem_type.split("_")

    # Add first type of traces to plot
    fig1.update_yaxes(title_text=f"{elements[elem_type[0]]['name']} in {elements[elem_type[0]]['unit']}",
                      secondary_y=False, range=elements[elem_type[0]]["range"], fixedrange=True)

    # Add all traces corresponding to the current element type
    for trace in (column for column in df.columns if elem_type[0] in column):
        trace_name = trace.replace(elem_type[0], elements[elem_type[0]]['name'])
        fig1.add_trace(
            go.Scattergl(name=trace_name, x=df["timestamp"], y=df[trace], legendgroup=elem_type[0],
                         mode="lines", marker_color=elements[elem_type[0]]["color"],
                         hovertemplate="%{y}" + elements[elem_type[0]]["unit"],
                         hoverlabel={"font_color": "white", "bordercolor": "white"}),
            secondary_y=False,
        )

        # Change min and max traces to dotted lines
        if "_min" in trace_name or "_max" in trace_name:
            fig1.update_traces(selector=dict(name=trace_name), line_dash="dot")

    # If there is a second element to plot add a second type of traces with a secondary y-axis
    if len(elem_type) > 1:
        fig1.update_yaxes(title_text=f"{elements[elem_type[1]]['name']} in {elements[elem_type[1]]['unit']}",
                          secondary_y=True, range=elements[elem_type[1]]["range"], fixedrange=True, tickmode="sync")

        # Add all traces corresponding to the current element type
        for trace in (column for column in df.columns if elem_type[1] in column):
            trace_name = trace.replace(elem_type[1], elements[elem_type[1]]['name'])
            fig1.add_trace(
                go.Scattergl(name=trace_name, x=df["timestamp"], y=df[trace], legendgroup=elem_type[1],
                             mode="lines", marker_color=elements[elem_type[1]]["color"],
                             hovertemplate="%{y}" + elements[elem_type[1]]["unit"],
                             hoverlabel={"font_color": "white", "bordercolor": "white"}),
                secondary_y=True,
            )

            # Change min and max traces to dotted lines
            if "_min" in trace_name or "_max" in trace_name:
                fig1.update_traces(selector=dict(name=trace_name), line_dash="dot")

    return fig1

# End page callbacks ------------------------------------------------------------------------------------------------
