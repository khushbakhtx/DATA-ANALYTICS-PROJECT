create or replace view sales_scatter as
select 
    p.product_id,
    p.product_name,
    s.unit_price,
    sum(s.quantity) as total_quantity_sold,
    avg(s.unit_price) over (partition by p.product_id) as avg_unit_price
from 
    sales s
join 
    product p on s.product_id = p.product_id
group by 
    p.product_id, p.product_name, s.unit_price;

select * from sales_scatter;