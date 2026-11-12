-- Modelo staging: padronizacao dos logs de cameras de monitoramento.

with source_data as (
    select * from {{ source('raw', 'cameras') }}
),

standardized as (
    select
        trim(cast(camera_event_id as varchar)) as camera_event_id,
        trim(cast(suspect_id as varchar)) as suspect_id,
        trim(cast(location_id as varchar)) as location_id,
        cast(seen_at as timestamp) as seen_at,
        upper(trim(cast(camera_label as varchar))) as camera_label
    from source_data
)

select * from standardized

