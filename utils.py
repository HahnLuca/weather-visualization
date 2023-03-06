# Studienarbeit
# Name: Luca Hahn
# Matrikelnr: 1923199
# Betreuer: Prof. Dr. Christof Hübner
# ------------------------------------------------------------------------------------------------------------------
# Usefull functions

from sqlalchemy import create_engine, exc, text


# Establish connection to database ----------------------------------------------------------------------------------
def connect_to_db(sql):
    constring = f"mysql+mysqlconnector://{sql['user']}:{sql['passwd']}@{sql['host']}/{sql['database']}"
    engine = create_engine(constring)
    try:
        with engine.connect() as con:
            con.execute(text("select 1"))
        print("Successfully connected to MySQL database")
    except exc.SQLAlchemyError as err:
        print(f"An error occured while trying to connect to MySQL database:\n{err.__cause__}")
    return engine
