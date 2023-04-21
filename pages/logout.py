# Studienarbeit
# HS Mannheim
# Fakultät Elektrotechnik
# Name: Luca Hahn
# Matrikelnr: 1923199
# Betreuer: Prof. Dr. Christof Hübner
# Abgabe: 21.04.2023
# ------------------------------------------------------------------------------------------------------------------
# Logout page with automatic redirection after logout

import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
from flask_login import logout_user, current_user

# Setup page to be used in multi-page app
dash.register_page(__name__, title="Logout", name="Logout")


# Logout page layout -------------------------------------------------------------------------------------------------
def layout():
    # Logout user if logged in
    if current_user.is_authenticated:
        logout_user()
        msg_logout = "Sie wurden erfolgreich ausgelogt."
    else:
        msg_logout = "Es ist kein Logout erforderlich, da Sie nicht angemeldet sind."

    return dbc.Row([
        dbc.Col([
            html.H5(msg_logout),
            html.Div(id="msg_redirect_logout"),
            dcc.Location(id="url_logout"),
            dcc.Interval(id="redirect_logout", interval=1 * 1000, n_intervals=0)
        ])
    ])
# End layout --------------------------------------------------------------------------------------------------------


# Page callbacks ----------------------------------------------------------------------------------------------------
# Redirect to dashboard after logout ---------------------------------------------------------------------------------
@callback(
    Output("msg_redirect_logout", "children"),
    Output("url_logout", "pathname"),
    Input("redirect_logout", "n_intervals"))
def update_loginout_button(n):
    if n < 3:
        return f"Automatische Weiterleitung in {3 - n} Sekunden.", dash.no_update
    else:
        return "Automatische Weiterleitung wird ausgeführt.", "/"
