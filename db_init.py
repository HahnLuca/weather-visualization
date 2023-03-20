# Studienarbeit
# Name: Luca Hahn
# Matrikelnr: 1923199
# Betreuer: Prof. Dr. Christof Hübner
# -------------------------------------------------------------------------------------------------------------------
# Database initialization
import pandas as pd
from sqlalchemy import URL, create_engine, MetaData, exc, text, Table, Column, \
    Integer, String, Float, Double, DateTime, Boolean
from werkzeug.security import generate_password_hash
import customtkinter as ctk
from config import table_stations, sql


if __name__ == "__main__":
    # Connect to database and test connection -----------------------------------------------------------------------
    # Connect to MySQL server
    url = URL.create(drivername=sql["drivername"], host=sql["host"],
                     username=sql["username"], password=sql["password"])
    engine = create_engine(url)
    meta = MetaData()

    try:
        # Create database if not exists
        with engine.connect() as con:
            dbs = con.execute(text("SHOW DATABASES"))
            dbs = [db[0] for db in dbs]
            if sql['database'] not in dbs:
                con.execute(text(f"CREATE DATABASE {sql['database']}"))
                print(f"Database {sql['database']} has been created")
            else:
                print(f"Database {sql['database']} already exists")

        # Update engine to be connected to database
        url = URL.create(drivername=sql["drivername"], username=sql["username"], password=sql["password"],
                         host=sql["host"], database=sql["database"])
        engine = create_engine(url)

        # Create necessary tables in database if not exist
        stations = Table(
            f"{table_stations}", meta,
            Column("ID", Integer, primary_key=True),
            Column("Name", String(30), nullable=False, unique=True),
            Column("Breitengrad", Double, nullable=False),
            Column("Längengrad", Double, nullable=False),
            Column("Hitzewarnung", Float, nullable=False),
            Column("Frostwarnung", Float, nullable=False)
        )
        warnings = Table(
            "warnings", meta,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("timestamp", DateTime, nullable=False),
            Column("station_ID", Integer, nullable=False),
            Column("warning_type", String(50), nullable=False),
            Column("trigger_temp", Float, nullable=False),
            Column("active", Boolean, nullable=False),
        )
        user = Table(
            "user", meta,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("username", String(64), nullable=False, unique=True),
            Column("pw_hash", String(128), nullable=False),
        )
        meta.create_all(engine)

        # Create first user to be able to log in and create new users
        while True:
            first_user = {"username": input("Please enter a username for dashboard access: "),
                          "pw_hash": input("Please enter a password for the user: ")}

            if first_user["username"] and first_user["pw_hash"]:
                first_user["pw_hash"] = generate_password_hash(first_user["pw_hash"])
                pd.DataFrame([first_user]).to_sql(name="user", con=engine, if_exists="append", index=False)
                print(f"The dashboard user {first_user['username']} has been created")
                break
            else:
                print("Incorrect inputs. Try again.")

        print("MySQL database has successfully been initialized")

    except exc.SQLAlchemyError as err:
        print(f"An error occured while trying to initialize MySQL database:\n{err.__cause__}")
