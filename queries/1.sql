create or replace view sales_scatter as
select 
    p.product_id,
    p.product_name,
    s.unit_price,
    sum(s.quantity) as total_quantity_sold,
    avg(s.unit_price) over (partition by p.product_id) as avg_unit_price,
    st.store_name
from 
    sales s
join product p on s.product_id = p.product_id
inner join store st on s.product_id = st.product_id
group by 
    p.product_id, p.product_name, s.unit_price, st.store_name;

select * from sales_scatter;
