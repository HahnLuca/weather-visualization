# Studienarbeit
# HS Mannheim
# Fakultät Elektrotechnik
# Name: Luca Hahn
# Matrikelnr: 1923199
# Betreuer: Prof. Dr. Christof Hübner
# Abgabe: 21.04.2023
# --------------------------------------------------------------------------------------------------------------------
# Here the database is initialized and the class User for managing the user data in database is defined

from sqlalchemy import URL, create_engine, MetaData, exc, text
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from config import sql

# Connect to database and verify connection --------------------------------------------------------------------------
db_url = URL.create(drivername=sql["drivername"], host=sql["host"], database=sql["database"],
                    username=sql["username"], password=sql["password"])
engine = create_engine(db_url)
meta = MetaData()
try:
    with engine.connect() as con:
        con.execute(text("select 1"))
    print("Successfully connected to database")
except exc.SQLAlchemyError as err:
    print(f"An error occured while trying to connect to database:\n{err.__cause__}")


# Define class for user management in database -----------------------------------------------------------------------
db = SQLAlchemy()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    pw_hash = db.Column(db.String(128), nullable=False)

    def __init__(self, username, pw):
        self.username = username
        # Password hashing to avoid storing passwords as plain text
        self.pw_hash = generate_password_hash(pw)

    def check_pw(self, pw):
        return check_password_hash(self.pw_hash, pw)
