create table product (
    product_id integer primary key,
    product_name varchar(255),
    supplier varchar(255),
    product_cost decimal(10, 2)
);

create table store (
    product_id integer references product(product_id),
    store_id integer primary key,
    store_name varchar(255),
    address varchar(255),
    neighborhood varchar(255),
    quantity_available integer
);

create table sales (
    sales_id integer primary key,
    product_id integer references product(product_id),
    sales_date date,
    unit_price decimal(10, 2),
    quantity integer
);