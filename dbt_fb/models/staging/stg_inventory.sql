with source as (
    select * from {{ ref('raw_inventory') }}
),
cleaned as (
    select
        record_id,
        outlet_id,
        item_sku,
        stock_on_hand::integer             as stock_on_hand,
        reorder_threshold::integer         as reorder_threshold,
        needs_reorder,
        unit_cost_gbp::numeric(10,2)       as unit_cost_gbp,
        last_updated::timestamp            as last_updated,
        supplier_name
    from source
    where record_id is not null
)
select * from cleaned
