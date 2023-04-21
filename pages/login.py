# Studienarbeit
# HS Mannheim
# Fakultät Elektrotechnik
# Name: Luca Hahn
# Matrikelnr: 1923199
# Betreuer: Prof. Dr. Christof Hübner
# Abgabe: 21.04.2023
# ------------------------------------------------------------------------------------------------------------------
# Login page with automatic redirection after login

import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from flask_login import current_user, login_user
from database import User

# Setup page to be used in multi-page app
dash.register_page(__name__, title="Login", name="Login")


# Login page layout --------------------------------------------------------------------------------------------------
def layout():
    # Redirect user if already logged in
    if current_user.is_authenticated:
        login_window = dbc.Row([
            dbc.Col([html.H5("Sie sind bereits eingelogt.")]),
            dcc.Interval(id="redirect_login", disabled=False, interval=1 * 1000, n_intervals=0)
        ])

    # Show user login window
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
# End layout --------------------------------------------------------------------------------------------------------


# Page callbacks ----------------------------------------------------------------------------------------------------
# Handle login tries and change input box colors --------------------------------------------------------------------
@callback(
    Output("input_user", "valid"),
    Output("input_user", "invalid"),
    Output("input_pw", "valid"),
    Output("input_pw", "invalid"),
    Output("msg_login", "children"),
    Output("redirect_login", "disabled"),
    Input("button_login", "n_clicks"),
    State("input_user", "value"),
    State("input_pw", "value"),
    prevent_initial_call=True)
def verify_login_try(n, username, pw):
    # Get user from database if user exists
    user = User.query.filter_by(username=username).first()
    if user:
        if pw is not None:
            # Verify password with hashed version in database
            if user.check_pw(pw):
                login_user(user)
                # Change colors of input boxes, display message and start redirection timer
                return True, False, True, False, "Login erfolgreich", False

        return True, False, False, True, "Falsches Passwort", True

    else:
        return False, True, False, False, "Falscher Benutzername", True


# Redirect to configurations page after login ------------------------------------------------------------------------
@callback(
    Output("msg_redirect_login", "children"),
    Output("url_login", "pathname"),
    Input("redirect_login", "n_intervals"),
    prevent_initial_call=True)
def handle_redirect(n):
    if n < 3:
        return f"Automatische Weiterleitung in {3 - n} Sekunden.", dash.no_update
    else:
        return "Automatische Weiterleitung wird ausgeführt.", "configurations"
