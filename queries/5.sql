create or replace view sales_distribution as
select 
    st.store_id,
    st.store_name,
    p.product_id,
    p.product_name,
    sum(s.unit_price * s.quantity) as total_sales,
    row_number() over (partition by st.store_id order by sum(s.unit_price * s.quantity) desc) as sales_rank
from 
    sales s
join product p on s.product_id = p.product_id
join store st on p.product_id = st.store_id
group by 
    st.store_id, st.store_name, p.product_id, p.product_name;
    
select * from sales_distribution;
