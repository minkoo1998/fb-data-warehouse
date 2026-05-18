with source as (
    select * from {{ ref('raw_pos_sales') }}
),
cleaned as (
    select
        order_id,
        outlet_id,
        item_sku,
        quantity::integer                  as quantity,
        unit_price::numeric(10,2)          as unit_price,
        line_total::numeric(10,2)          as line_total,
        order_ts::timestamp                as order_ts,
        order_date::date                   as order_date
    from source
    where order_id is not null
      and quantity > 0
      and unit_price > 0
)
select * from cleaned
