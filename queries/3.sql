create or replace view sales_trends as
select 
    cast(s.sales_date as date) as sales_date,
    sum(s.unit_price * s.quantity) as total_sales,
    date_trunc('month', s.sales_date) as sales_month
from 
    sales s
group by 
    s.sales_date
order by 
    sales_month;

select * from sales_trends;