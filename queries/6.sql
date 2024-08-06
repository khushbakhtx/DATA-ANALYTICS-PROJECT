create or replace view sales_3d_analysis as
select 
    s.sales_date,
    st.store_id,
    st.store_name,
    p.product_id,
    p.product_name,
    sum(s.quantity) as total_quantity_sold,
    rank() over (partition by st.store_id order by sum(s.quantity) desc) as product_rank
from 
    sales s
join store st on s.product_id = st.store_id
join product p on s.product_id = p.product_id
group by 
    s.sales_date, st.store_id, st.store_name, p.product_id, p.product_name
order by 
    s.sales_date, st.store_id, p.product_id;

select * from sales_3d_analysis;
