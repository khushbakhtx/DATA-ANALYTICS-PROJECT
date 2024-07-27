from sqlalchemy import create_engine

def set_connection():
    with open('credentials.txt', 'r') as f:
        db_string=f.read()  
    engine=create_engine(db_string)
    return engine.connect()