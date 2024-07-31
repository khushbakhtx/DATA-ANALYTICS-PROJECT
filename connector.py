from sqlalchemy import create_engine, text
import duckdb
import sqlite3

def get_credentials(db_type):
    credentials=''
    if db_type=='postgres':
        with open('credentials.txt', 'r') as f:
            credentials=f.read()
    elif db_type=='duckdb':
        credentials='my.db'
    elif db_type == 'sqlite':
        credentials = 'sqlite.db'
    return credentials


def set_connection(db_type):
    credentials=get_credentials(db_type)
    if db_type=='postgres':
        engine=create_engine(credentials)
        return engine.connect()
    elif db_type=='duckdb':
        return duckdb.connect(credentials)
    elif db_type == 'sqlite':
        return sqlite3.connect(credentials)