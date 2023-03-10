# Studienarbeit
# Name: Luca Hahn
# Matrikelnr: 1923199
# Betreuer: Prof. Dr. Christof Hübner
# ------------------------------------------------------------------------------------------------------------------
# Database configurations and connection establishment

from sqlalchemy import URL, create_engine, MetaData, exc, text
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Name of table in database storing all the weather stations
table_stations = "wetterstationen"

# Connect to database and test connection ----------------------------------------------------------------------------
db_url = URL.create(drivername="mysql", username="student", password="student",
                    host="localhost", database="wetterstationen")
engine = create_engine(db_url)
meta = MetaData()
try:
    with engine.connect() as con:
        con.execute(text("select 1"))
    print("Successfully connected to MySQL database")
except exc.SQLAlchemyError as err:
    print(f"An error occured while trying to connect to MySQL database:\n{err.__cause__}")


# Define class for user management in database -----------------------------------------------------------------------
db = SQLAlchemy()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    pw_hash = db.Column(db.String(128), nullable=False)

    def __init__(self, username, pw):
        self.username = username
        # Safe only hashed versions of user passwords
        self.pw_hash = generate_password_hash(pw)

    def check_pw(self, pw):
        return check_password_hash(self.pw_hash, pw)
