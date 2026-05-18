with invoices as (
    select * from {{ ref('stg_supplier_invoices') }}
),
cogs as (
    select
        invoice_date,
        supplier_name,
        item_sku,
        sum(units_received)             as total_units_received,
        sum(total_cost_gbp)             as total_cost_gbp,
        avg(unit_cost_gbp)              as avg_unit_cost
    from invoices
    group by 1, 2, 3
)
select * from cogs
