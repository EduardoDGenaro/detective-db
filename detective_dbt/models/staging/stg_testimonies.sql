-- Modelo staging: padronizacao dos depoimentos colhidos e alibis estruturados.

with source_data as (
    select * from {{ source('raw', 'testimonies') }}
),

standardized as (
    select
        trim(cast(testimony_id as varchar)) as testimony_id,
        trim(cast(suspect_id as varchar)) as suspect_id,
        trim(cast(statement as varchar)) as statement,
        cast(statement_time as timestamp) as statement_time,
        trim(cast(claimed_location_id as varchar)) as claimed_location_id,
        cast(claimed_event_time as timestamp) as claimed_event_time,
        cast(consistency_flag as boolean) as consistency_flag
    from source_data
)

select * from standardized

