# Studienarbeit
# Name: Luca Hahn
# Matrikelnr: 1923199
# Betreuer: Prof. Dr. Christof Hübner
# ------------------------------------------------------------------------------------------------------------------
# Restricted settings page

import dash
from dash import html, dcc, callback, Input, Output, State, dash_table, ctx
import dash_bootstrap_components as dbc
from flask_login import current_user
import pandas as pd
from utils import connect_to_db
import config

dash.register_page(__name__, title="Konfigurieren", name="Konfigurieren")
engine = connect_to_db(config.sql)
with engine.connect() as con_load:
    df_load = pd.read_sql_table("wetterstationen", con=con_load, index_col="id")


# Page layout -------------------------------------------------------------------------------------------------------
def layout():
    if not current_user.is_authenticated:
        return dbc.Row([
            dbc.Col([
                html.H5(["Zugriff verweigert, bitte ", html.A("einloggen", href="login"), "!"])
            ])
        ])
    else:
        return dbc.Row([
            dbc.Col([
                html.H5("Wetterstationen konfigurieren:", className="mb-2"),
                dash_table.DataTable(
                    id="table",
                    columns=[{"name": i, "id": i} for i in df_load.columns],
                    data=df_load.to_dict('records'),
                    editable=True,
                    sort_action="native",
                    sort_mode="single",
                    row_deletable=True,
                    page_action="native",
                    page_current=0,
                    page_size=10,
                ),
                html.Div([
                    dbc.Button("Wetterstation anlegen", id="table_new_station", type="submit", className="mt-2 me-2"),
                    dbc.Button("Änderungen verwerfen", id="table_reset", type="reset", className="mt-2 me-2"),
                    dbc.Button("Änderungen übernehmen", id="table_confirm", type="submit", className="mt-2 me-2"),
                ], className="d-grid d-md-flex justify-content-md-end"),

                html.Div(id="table_msg")
            ])
        ])


@callback(
    Output("table", "data"),
    Output("table_msg", "children"),
    Input("table_new_station", "n_clicks"),
    Input("table_reset", "n_clicks"),
    Input("table_confirm", "n_clicks"),
    State("table", "data"),
    State("table", "columns"))
def update_database(n_new_station, n_reset, n_confirm, rows, columns):
    with engine.connect() as con:
        if "table_confirm" == ctx.triggered_id:
            df = pd.DataFrame(rows)
            df.to_sql(name="wetterstationen", con=engine, if_exists="replace", index=True, index_label="id")
            msg = "Änderungen in Datenbank übernommen"
        elif "table_new_station" == ctx.triggered_id:
            rows.append({c["id"]: "" for c in columns})
            msg = "Neue Wetterstation kann angelegt werden"
        else:
            df = pd.read_sql_table("wetterstationen", con=con, index_col="id")
            rows = df.to_dict("records")
            if "table_reset" == ctx.triggered_id:
                msg = "Änderungen wurden verworfen"
            else:
                msg = ""

    return rows, msg
