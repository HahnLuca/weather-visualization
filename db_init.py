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
            Column("Hitzewarnung", Float),
            Column("Frostwarnung", Float)
        )
        warnings = Table(
            "warnings", meta,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("timestamp", DateTime, nullable=False),
            Column("station", String(30), nullable=False),
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

        # Create first user to be able to log in and create new users -----------------------------------------------
        # Insert user to table in database
        def create_user():
            if first_user.get() and first_user_pw.get():
                user_init = {"username": first_user.get(), "pw_hash": generate_password_hash(first_user_pw.get())}
                pd.DataFrame([user_init]).to_sql(name="user", con=engine, if_exists="append", index=False)
                print(f"The dashboard user {first_user.get()} has been created")
                app.destroy()
            else:
                first_user.delete(0, ctk.END)
                first_user.configure(placeholder_text="Benutzernamen eingeben")
                first_user_pw.delete(0, ctk.END)
                first_user_pw.configure(placeholder_text="Passwort eingeben")
                warning.configure(text="Fehlerhafte Eingabe")

        # Initialize input window
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("green")
        app = ctk.CTk()
        app.geometry("400x300")
        app.title("Ersten Benutzer anlegen")

        # Fill window with text, input fields and a button
        frame = ctk.CTkFrame(master=app)
        frame.pack(pady=20, padx=20, fill="both", expand=True)
        label = ctk.CTkLabel(master=frame, wraplength=300, justify="center",
                             text="Um Zugriff auf das Dashboard zu haben, "
                                  "ist es notwendig einen Benutzer anzulegen.")
        label.pack(pady=12, padx=5)
        first_user = ctk.CTkEntry(master=frame, placeholder_text="Benutzernamen angeben", width=250)
        first_user.pack(pady=12, padx=5)
        first_user_pw = ctk.CTkEntry(master=frame, placeholder_text="Passwort angeben", width=250)
        first_user_pw.pack(pady=12, padx=5)
        button = ctk.CTkButton(master=frame, text="Bestätigen", command=create_user, width=250)
        button.pack(pady=12, padx=5)
        warning = ctk.CTkLabel(master=frame, text="")
        warning.pack(pady=12, padx=5)

        app.mainloop()
        # End user creation -----------------------------------------------------------------------------------------

        print("MySQL database has been initialized successfully")

    except exc.SQLAlchemyError as err:
        print(f"An error occured while trying to initialize MySQL database:\n{err.__cause__}")
