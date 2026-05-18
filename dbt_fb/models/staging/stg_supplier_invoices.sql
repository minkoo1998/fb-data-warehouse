with source as (
    select * from {{ ref('raw_supplier_invoices') }}
),
cleaned as (
    select
        invoice_id,
        supplier_name,
        item_sku,
        units_received::integer            as units_received,
        unit_cost_gbp::numeric(10,2)       as unit_cost_gbp,
        total_cost_gbp::numeric(10,2)      as total_cost_gbp,
        invoice_date::date                 as invoice_date,
        payment_status
    from source
    where invoice_id is not null
)
select * from cleaned
