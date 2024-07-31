import pandas as pd
from connector import set_connection

def read_query(query_name):
    with open(f'queries/{query_name}.sql') as f:
        return f.read()
    
def get_data(query_name):
    query=read_query(query_name)
    with set_connection('duckdb') as ps:
        return pd.read_sql(query, ps)