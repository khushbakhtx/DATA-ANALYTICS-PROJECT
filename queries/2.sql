create or replace view total_sales_by_product as
select 
    p.product_id,
    p.product_name,
    sum(s.unit_price * s.quantity) as total_sales,
    count(s.sales_id) as total_transactions
from 
    sales s
join 
    product p on s.product_id = p.product_id
group by 
    p.product_id, p.product_name
order by 
    total_sales desc;

select * from total_sales_by_product;