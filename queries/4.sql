create or replace view product_market_share as
select 
    p.product_id,
    p.product_name,
    sum(s.unit_price * s.quantity) as total_sales,
    round(sum(s.unit_price * s.quantity) / (select sum(unit_price * quantity) from sales) * 100, 2) as market_share_percentage
from 
    sales s
join 
    product p on s.product_id = p.product_id
group by 
    p.product_id, p.product_name;

select * from product_market_share;