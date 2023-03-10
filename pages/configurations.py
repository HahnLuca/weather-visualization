# Studienarbeit
# Name: Luca Hahn
# Matrikelnr: 1923199
# Betreuer: Prof. Dr. Christof Hübner
# ------------------------------------------------------------------------------------------------------------------
# Restricted settings page

import dash
from dash import html, callback, Input, Output, State, dash_table, ctx
import dash_bootstrap_components as dbc
from flask_login import current_user
import pandas as pd
from sqlalchemy import text, inspect, Table, Column, Integer, Float, String, DateTime, exc
from database import engine, meta, User, db
from mqtt_handler import mqtt_client

dash.register_page(__name__, title="Konfigurieren", name="Konfigurieren")


# Page layout -------------------------------------------------------------------------------------------------------
def layout():
    # Block page if user is not authenticated
    if not current_user.is_authenticated:
        return dbc.Row([
            dbc.Col([
                html.H5(["Zugriff verweigert, bitte ", html.A("einloggen", href="login"), "!"])
            ])
        ])
    else:
        return dbc.Row([
            # Part DataTable
            dbc.Row([
                dbc.Col([
                    html.H5("Wetterstationen konfigurieren:", className="mb-2"),
                    dash_table.DataTable(id="table", editable=True, sort_action="native", sort_mode="single",
                                         row_deletable=True, page_action="native", page_current=0, page_size=10),
                    html.Div([
                        dbc.Button("Wetterstation anlegen", id="table_new_station", type="submit", className="mt-2 me-2"),
                        dbc.Button("Änderungen verwerfen", id="table_reset", type="reset", className="mt-2 me-2"),
                        dbc.Button("Änderungen übernehmen", id="table_confirm", type="submit", className="mt-2 me-2"),
                    ], className="d-grid d-md-flex justify-content-md-end"),
                    html.Div(id="table_msg", className="mt-2")
                ])
            ]),
            # Part new user registration
            dbc.Row([
                dbc.Col([html.H5("Neuen Benutzer anlegen:")]),
                dbc.Row([
                    dbc.Col([dbc.Input(id="new_user", placeholder="Benutzername eingeben", type="text")],
                            xs=12, sm=12, md=4, lg=4, xl=4, xxl=4, className="mt-2"),
                    dbc.Col([dbc.Input(id="new_pw", placeholder="Passwort eingeben", type="password")],
                            xs=12, sm=12, md=4, lg=4, xl=4, xxl=4, className="mt-2"),
                    dbc.Col([dbc.Button("Bestätigen", id="button_new_user", n_clicks=0, type="submit")],
                            xs=12, sm=12, md=4, lg=4, xl=4, xxl=4, className="mt-2")
                ]),
                dbc.Col([html.Div(id="new_user_msg", className="mt-2")])
            ], className="mt-4")
        ])
# End page layout ---------------------------------------------------------------------------------------------------


# Page callbacks ----------------------------------------------------------------------------------------------------
# Load the DataTable or add a new line depending on which button has been pressed -----------------------------------
@callback(
    Output("table", "data"),
    Output("table", "columns"),
    Input("table_new_station", "n_clicks"),
    Input("table_reset", "n_clicks"),
    State("table", "data"),
    State("table", "columns"))
def update_datatable(n_new_station, n_reset, rows, columns):
    # "New station" button pressed
    if "table_new_station" == ctx.triggered_id:
        rows.append({c["id"]: "" for c in columns})

    # "Discard changes" button pressed or initial callback
    else:
        # Read last saved data from database
        with engine.connect() as con:
            df = pd.read_sql_table("wetterstationen", con=con, index_col="id")
        rows = df.to_dict("records")
        columns = [{"name": i, "id": i} for i in df.columns]

    # TODO delete old messages from Confirm button
    return rows, columns


# Save changes made in the DataTable to the database ---------------------------------------------------------------
@callback(
    Output("table_msg", "children"),
    Input("table_confirm", "n_clicks"),
    State("table", "data"),
    prevent_initial_call=True)
def update_database(n_confirm, rows):
    df_stations = pd.DataFrame(rows)
    with engine.connect() as con:
        # Try saving DataTable to an empty copy of the MySQL table to check if DataTable is valid
        con.execute(text("CREATE TABLE wetterstationen_temp LIKE wetterstationen"))
        try:
            df_stations.to_sql(name="wetterstationen_temp", con=engine, if_exists="append", index=False)
            con.execute(text("DROP TABLE wetterstationen_temp"))
            # If check was succesful truncate original table and save new DataTable
            con.execute(text("TRUNCATE TABLE wetterstationen"))
            df_stations.to_sql(name="wetterstationen", con=engine, if_exists="append", index=False)
        except exc.SQLAlchemyError:
            # If check failed drop temporary table and end function
            con.execute(text("DROP TABLE wetterstationen_temp"))
            return "Fehlerhafte Eingabe, Tabelle konnte nicht übernommen werden!"

    # Create a new table in database for every added station
    # TODO implement general data format
    for station in df_stations["sql_table"]:
        if not inspect(engine).has_table(station):
            Table(
                station, meta,
                Column("data_id", Integer, primary_key=True),
                Column("datetime", DateTime),
                Column("devicename", String(50)),
                Column("timestamp", DateTime),
                Column("temperature", Float),
                Column("humidity", Float),
                Column("rain", Float),
                Column("winddirection", Float),
                Column("windspeed", Float),
                Column("rssi", Float),
            )
    meta.create_all(engine)

    # Update MQTT subscriptions
    mqtt_client.unsubscribe("#")
    topics = [(topic, 0) for topic in df_stations["mqtt_topic"]]
    mqtt_client.subscribe(topics)

    return "Änderungen in Datenbank übernommen."


# Add new user to database ------------------------------------------------------------------------------------------
@callback(
    Output("new_user_msg", "children"),
    Output("new_user", "value"),
    Output("new_pw", "value"),
    Input("button_new_user", "n_clicks"),
    State("new_user", "value"),
    State("new_pw", "value"),
    prevent_initial_call=True)
def create_new_user(n_new_user, username, pw):
    # Check if username is not available anymore
    user = User.query.filter_by(username=username).first()
    if user is not None:
        return "Benutzername bereits vergeben", username, pw

    # Add user to database and clear inputs
    elif username is not None and pw is not None:
        new_user = User(username, pw)
        db.session.add(new_user)
        db.session.commit()
        return f"Neuer Benutzer {username} wurde angelegt", "", ""

    else:
        return "Fehlerhafte Eingabe", username, pw
