# Studienarbeit
# HS Mannheim
# Fakultät Elektrotechnik
# Name: Luca Hahn
# Matrikelnr: 1923199
# Betreuer: Prof. Dr. Christof Hübner
# Abgabe: 21.04.2023
# -------------------------------------------------------------------------------------------------------------------
# Main script setting up the general layout with navigation bar and starting the application

import dash
from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import os
from flask import Flask
from flask_login import LoginManager, current_user
from database import User, db, db_url
from mqtt_handler import mqtt_client


# Configure the Dash server -----------------------------------------------------------------------------------------
server = Flask(__name__)
app = Dash(__name__, server=server, use_pages=True, suppress_callback_exceptions=True,
           external_stylesheets=[dbc.themes.SANDSTONE, dbc.icons.BOOTSTRAP])
server.config.update(
    # Secret key necessary to handle user sessions
    SECRET_KEY=os.urandom(12),
    SQLALCHEMY_DATABASE_URI=db_url,
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)
db.init_app(server)

# Configure the LoginManager ----------------------------------------------------------------------------------------
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = "/login"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# General layout ----------------------------------------------------------------------------------------------------
app.layout = dbc.Container([
    dbc.Navbar(
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.A([
                        html.Img(
                            alt="Logo Hochschule Mannheim",
                            src="assets/HSMA_Logo_weiß.png",
                            height="30px"
                        )],
                        href="https://www.et.hs-mannheim.de/",
                        target="_blank"
                    ),
                ]),
                dbc.Col([
                    dbc.NavbarBrand("Dashboard Umweltdaten"),
                ])
            ]),
            dbc.NavbarToggler(id="navbar_toggler"),
            dbc.Collapse(
                dbc.Nav([
                    # dbc elements are wrapped inside an html.A to prevent errors when changing pages quikly (bug?)
                    dbc.NavItem(html.A(dbc.NavLink("Dashboard"), href="/",
                                       style={"text-decoration-line": "none"})),
                    dbc.NavItem(html.A(dbc.NavLink("Verwaltung"), href="configurations",
                                       style={"text-decoration-line": "none"})),
                    html.A(dbc.Button("Login", id="button_loginout"), id="button_loginout_link")
                ], className="ms-auto", navbar=True),
                id="navbar_collapse",
                navbar=True,
            ),
        ], fluid=True), className="mb-3", color="steelblue", dark=True,
    ),
    # Contents of current page are added to the general layout
    dash.page_container,
    dcc.Location(id="url")
], fluid=True)
# End general layout ------------------------------------------------------------------------------------------------


# General callbacks -------------------------------------------------------------------------------------------------
# Handle navigation bar collapse on small screens -------------------------------------------------------------------
@app.callback(
    Output("navbar_collapse", "is_open"),
    Input("navbar_toggler", "n_clicks"),
    State("navbar_collapse", "is_open"))
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    else:
        return is_open


# Display correct login/logout button depending on login status -----------------------------------------------------
@app.callback(
    Output("button_loginout", "children"),
    Output("button_loginout_link", "href"),
    Input("url", "pathname"))
def update_loginout_button(path):
    if current_user.is_authenticated:
        return "Logout", "logout"
    else:
        return "Login", "login"
# End general callbacks ---------------------------------------------------------------------------------------------


if __name__ == '__main__':
    mqtt_client.loop_start()
    # Change debug to True if you are working on the code
    # Note: If app is running in debug mode message is printed multiple times
    #       -> Comment out the print statements in the MQTT callbacks in this case
    app.run_server(debug=False)
