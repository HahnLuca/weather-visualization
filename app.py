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
from flask_login import login_user, LoginManager, UserMixin, current_user

server = Flask(__name__)
app = Dash(__name__, server=server, use_pages=True, suppress_callback_exceptions=True,
           external_stylesheets=[dbc.themes.SANDSTONE, dbc.icons.BOOTSTRAP])
user_pw_combo = {"student": "student"}
server.config.update(SECRET_KEY=os.urandom(12))

login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = "/login"


class User(UserMixin):
    def __init__(self, username):
        self.id = username


@login_manager.user_loader
def load_user(username):
    """This function loads the user by user id. Typically this looks up the user from a user database.
    We won't be registering or looking up users in this example, since we'll just login using LDAP server.
    So we'll simply return a User object with the passed in username.
    """
    return User(username)


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


# Handle login tries ------------------------------------------------------------------------------------------------
@app.callback(
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
def verify_login_try(n, user, pw):
    if user_pw_combo.get(user) is None:
        return False, True, False, False, "Falscher Benutzername", True
    elif user_pw_combo.get(user) == pw:
        login_user(User(user))
        return True, False, True, False, "Login erfolgreich", False
    else:
        return True, False, False, True, "Falsches Passwort", True


# End general callbacks ---------------------------------------------------------------------------------------------


if __name__ == '__main__':
    app.run_server(debug=True)
