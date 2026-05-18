{{ config(materialized='table') }}

with daily as (
    select * from {{ ref('int_daily_sales') }}
),
revenue as (
    select
        order_date,
        outlet_id,
        sum(total_revenue)              as daily_revenue_gbp,
        sum(order_count)                as order_count,
        sum(total_quantity)             as items_sold,
        round(sum(total_revenue) /
            nullif(sum(order_count),0), 2) as avg_order_value
    from daily
    group by 1, 2
)
select
    *,
    sum(daily_revenue_gbp) over (
        partition by outlet_id
        order by order_date
        rows between unbounded preceding and current row
    ) as cumulative_revenue
from revenue
order by order_date desc, outlet_id
