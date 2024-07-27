import pandas as pd
from sqlalchemy import text
from connector import set_connection

schema_name = 'walmart'
schema_creation_activation = f"""
create schema if not exists {schema_name};
set search_path to {schema_name};
"""

product_1 = '''
create table if not exists product(
	product_key serial primary key,
	product varchar(150) not null,
	standard_cost varchar(50) not null,
	color varchar(50),
	subcategory varchar(100),
	category varchar(100),
	background_color_format varchar(50),
	font_color_format varchar(50)
)
'''
sales_2 = '''
create table if not exists region(
	sales_territory_key serial primary key,
	region text,
	country varchar(100),
	group_ varchar(100)
)
'''
store_3 = '''
create table if not exists reseller(
	reseller_key serial primary key,
	business_type varchar(150),
	reseller varchar(150),
	city varchar(50),
	state_province varchar(50),
	country_region varchar(50)
)
'''

files = [
    './source/product.csv', 
    './source/sales.csv',
    './source/store.csv'
]


with set_connection() as ps:
    ps.execute(text(schema_creation_activation)),
    ps.execute(text(product_1)),
    ps.execute(text(sales_2)),
    ps.execute(text(store_3)),
    ps.commit()


df_product = pd.read_csv('./source/product.csv', sep='\t')
df_sales = pd.read_csv('./source/sales.csv', sep='\t')
df_store = pd.read_csv('./source/store.csv', sep='\t')

df_product.rename(columns={
    'ProductKey': 'product_key', 
    'Product': 'product', 
    'Standard Cost': 'standard_cost', 
    'Color': 'color', 
    'Subcategory': 'subcategory',
    'Category': 'category', 
    'Background Color Format': 'background_color_format', 
    'Font Color Format': 'font_color_format'
}, inplace=True)

# make the same thing with the rest tables

with set_connection() as ps:
    df_product.to_sql(name='product', schema='walmart', con=ps, if_exists='append', index=False)
    df_sales.to_sql(name='sales', schema='walmart', con=ps, if_exists='append', index=False)
    df_store.to_sql(name='store', schema='walmart', con=ps, if_exists='append', index=False)
    ps.commit()


     
