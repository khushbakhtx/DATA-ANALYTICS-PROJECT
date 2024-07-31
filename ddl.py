import pandas as pd
from sqlalchemy import text
from connector import set_connection

with open('./queries/ddl.sql') as f:
    query=f.read()
# with open('./queries/ddl.sql') as f:
#     ddl_queries = f.read().split(';')

with set_connection('duckdb') as duck:
    # for query in ddl_queries:
    #     query = query.strip()
    #     if query:
    #         duck.execute(query)
    duck.execute(query),
    df_product = pd.read_csv('./source/product.csv')
    df_sales = pd.read_csv('./source/sales.csv')
    df_store = pd.read_csv('./source/store.csv')
    df_product.rename(columns={
        'ProductId': 'product_id',
        'ProductName': 'product_name',
        'Supplier': 'supplier',
        'ProductCost': 'product_cost'
    }, inplace=True)
    df_store.rename(columns={
        'ProductId': 'product_id',
        'StoreId': 'store_id',
        'StoreName': 'store_name',
        'Address': 'address',
        'neighborhood': 'neighborhood',
        'QuantityAvailable': 'quantity_available'
    }, inplace=True)
    df_sales.rename(columns={
        'SalesId': 'sales_id',
        'StoreId': 'store_id',
        'ProductId': 'product_id',
        'Date': 'sales_date',
        'UnitPrice': 'unit_price',
        'Quantity': 'quantity'
    }, inplace=True)
    # df_product.to_sql('product', duck, if_exists='append', index=False)
    # df_store.to_sql('store', duck, if_exists='append', index=False)
    # df_sales.to_sql('sales', duck, if_exists='append', index=False)
    duck.query("""
        insert into product
        select *
        from df_product
    """)
    duck.query("""
        insert into store
        select *
        from df_store
    """)
    duck.query("""
        insert into sales
        select *
        from df_sales
    """)   
     
