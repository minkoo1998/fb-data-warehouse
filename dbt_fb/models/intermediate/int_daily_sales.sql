with pos as (
    select * from {{ ref('stg_pos_sales') }}
),
daily as (
    select
        order_date,
        outlet_id,
        item_sku,
        count(distinct order_id)        as order_count,
        sum(quantity)                   as total_quantity,
        sum(line_total)                 as total_revenue
    from pos
    group by 1, 2, 3
)
select * from daily
