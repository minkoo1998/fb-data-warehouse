{{ config(materialized='table') }}

with inventory as (
    select * from {{ ref('stg_inventory') }}
),
sales as (
    select
        item_sku,
        round(avg(total_quantity), 0)   as avg_daily_units_sold
    from {{ ref('int_daily_sales') }}
    group by 1
),
joined as (
    select
        i.outlet_id,
        i.item_sku,
        i.supplier_name,
        i.stock_on_hand,
        i.reorder_threshold,
        i.needs_reorder,
        i.unit_cost_gbp,
        s.avg_daily_units_sold,
        case
            when s.avg_daily_units_sold > 0
            then round(i.stock_on_hand / s.avg_daily_units_sold, 1)
            else null
        end                             as days_cover_remaining,
        round(i.stock_on_hand * i.unit_cost_gbp, 2) as stock_value_gbp
    from inventory i
    left join sales s using (item_sku)
)
select * from joined
order by days_cover_remaining asc
