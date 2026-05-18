{{ config(materialized='table') }}

with revenue as (
    select
        item_sku,
        sum(total_revenue)              as total_revenue_gbp
    from {{ ref('int_daily_sales') }}
    group by 1
),
cogs as (
    select
        item_sku,
        sum(total_cost_gbp)             as total_cost_gbp
    from {{ ref('int_cogs_matched') }}
    group by 1
),
joined as (
    select
        r.item_sku,
        r.total_revenue_gbp,
        c.total_cost_gbp,
        round(r.total_revenue_gbp - c.total_cost_gbp, 2)           as gross_profit_gbp,
        round((r.total_revenue_gbp - c.total_cost_gbp)
            / nullif(r.total_revenue_gbp, 0) * 100, 1)             as gross_margin_pct
    from revenue r
    left join cogs c using (item_sku)
)
select * from joined
order by gross_margin_pct desc
