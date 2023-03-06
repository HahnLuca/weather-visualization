# Studienarbeit
# Name: Luca Hahn
# Matrikelnr: 1923199
# Betreuer: Prof. Dr. Christof Hübner
# ------------------------------------------------------------------------------------------------------------------
# Login page

import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
from flask_login import current_user

dash.register_page(__name__, title="Login", name="Login")


# Login page layout --------------------------------------------------------------------------------------------------
def layout():
    # Cover user entering the page while already beeing logged in
    if current_user.is_authenticated:
        login_window = dbc.Row([
            dbc.Col([html.H5("Sie sind bereits eingelogt.")]),
            dcc.Interval(id="redirect_login", disabled=False, interval=1 * 1000, n_intervals=0)
        ])
    # User login window
    else:
        login_window = dbc.Row([
            dbc.Col([html.H5("Bitte Anmeldedaten eingeben:")]),
            dbc.Row([
                dbc.Col([dbc.Input(id="input_user", placeholder="Benutzername eingeben", type="text")],
                        xs=12, sm=12, md=4, lg=4, xl=4, xxl=4, className="mt-2"),
                dbc.Col([dbc.Input(id="input_pw", placeholder="Passwort eingeben", type="password")],
                        xs=12, sm=12, md=4, lg=4, xl=4, xxl=4, className="mt-2"),
                dbc.Col([dbc.Button("Login", id="button_login", n_clicks=0, type="submit")],
                        xs=12, sm=12, md=4, lg=4, xl=4, xxl=4, className="mt-2")
            ]),
            dcc.Interval(id="redirect_login", disabled=True, interval=1 * 1000, n_intervals=0)
        ])

    return dbc.Row([
        dbc.Col([
            login_window,
            html.Div(id="msg_login", className="mt-1"),
            html.Div(id="msg_redirect_login", className="mt-1"),
            dcc.Location(id="url_login")
        ])
    ])


# Redirect to configurations page after login ------------------------------------------------------------------------
@callback(
    Output("msg_redirect_login", "children"),
    Output("url_login", "pathname"),
    Input("redirect_login", "n_intervals"),
    prevent_initial_call=True)
def update_loginout_button(n):
    if n < 3:
        return f"Automatische Weiterleitung in {3 - n} Sekunden.", dash.no_update
    else:
        return "Automatische Weiterleitung wird ausgeführt.", "configurations"
