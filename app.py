# Studienarbeit
# Name: Luca Hahn
# Matrikelnr: 1923199
# Betreuer: Prof. Dr. Christof Hübner
# -------------------------------------------------------------------------------------------------------------------
# Main script

import dash
from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import os
from flask import Flask
from flask_login import LoginManager, current_user
from database import User, db, db_url
from mqtt_handler import mqtt_client


# Configure the Dash server
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

# Configure the LoginManager
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = "/login"


# Callback for reloading the user when refreshing the page
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
                        href="https://www.hs-mannheim.de/",
                        target="_blank"
                    ),
                ]),
                dbc.Col([
                    dbc.NavbarBrand("Wetter auf der BUGA 2023"),
                ])
            ]),
            dbc.NavbarToggler(id="navbar_toggler"),
            dbc.Collapse(
                dbc.Nav([
                    # dbc elements wrapped inside an html.A to prevent errors when changing pages quikly (bug?)
                    dbc.NavItem(html.A(dbc.NavLink("Dashboard"), href="/",
                                       style={"text-decoration-line": "none"})),
                    dbc.NavItem(html.A(dbc.NavLink("Konfigurieren"), href="configurations",
                                       style={"text-decoration-line": "none"})),
                    html.A(dbc.Button("Login", id="button_loginout"), id="button_loginout_link")
                ], className="ms-auto", navbar=True),
                id="navbar_collapse",
                navbar=True,
            ),
        ]), className="mb-3", color="steelblue", dark=True,
    ),
    dash.page_container,
    dcc.Location(id="url")
])
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
    # TODO set debug=False when app is finished
    app.run_server(debug=True)
