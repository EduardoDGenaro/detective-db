-- Tabela fato de eventos de cameras de monitoramento.
-- Utiliza funcoes de janela (LAG e ROW_NUMBER) para rastrear deslocamentos
-- sequenciais de cada suspeito entre ambientes da Mansao Valmont.

with cameras as (
    select * from {{ ref('stg_cameras') }}
),

suspects as (
    select * from {{ ref('dim_suspects') }}
),

locations as (
    select * from {{ ref('dim_locations') }}
),

enriched as (
    select
        c.camera_event_id,
        c.suspect_id,
        s.suspect_name,
        c.location_id,
        l.location_name,
        l.area_type,
        l.city_zone,
        l.is_restricted_zone as is_suspicious_location_event,
        l.security_tier,
        c.seen_at,
        c.camera_label,
        row_number() over (
            partition by c.suspect_id
            order by c.seen_at asc, c.camera_event_id asc
        ) as suspect_event_sequence,
        lag(c.location_id) over (
            partition by c.suspect_id
            order by c.seen_at asc, c.camera_event_id asc
        ) as previous_location_id,
        lag(l.location_name) over (
            partition by c.suspect_id
            order by c.seen_at asc, c.camera_event_id asc
        ) as previous_location_name,
        lag(c.seen_at) over (
            partition by c.suspect_id
            order by c.seen_at asc, c.camera_event_id asc
        ) as previous_seen_at
    from cameras c
    left join suspects s
        on c.suspect_id = s.suspect_id
    left join locations l
        on c.location_id = l.location_id
)

select
    *,
    case
        when previous_seen_at is not null
        then date_diff('minute', previous_seen_at, seen_at)
        else null
    end as minutes_since_previous_sighting
from enriched
