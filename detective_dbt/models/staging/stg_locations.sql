-- Modelo staging: padronizacao dos ambientes monitorados na Mansao Valmont.

with source_data as (
    select * from {{ source('raw', 'locations') }}
),

standardized as (
    select
        trim(cast(location_id as varchar)) as location_id,
        trim(cast(location_name as varchar)) as location_name,
        upper(trim(cast(area_type as varchar))) as area_type,
        trim(cast(city_zone as varchar)) as city_zone
    from source_data
)

select * from standardized

