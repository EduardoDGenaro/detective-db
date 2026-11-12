-- Teste personalizado: verifica a consistencia temporal da coleta de evidencias.
-- Regra de validade temporal para a base didática e os casos randomizados:
--   1. Nenhuma evidencia pode ter `collected_at` anterior ao primeiro registro de camera
--      da noite do crime.
--   2. Nenhuma evidencia pode ter `collected_at` posterior ao encerramento da janela
--      pericial inicial do caso (18h do dia seguinte ao primeiro registro).
-- No dbt, o teste passa quando a consulta retorna 0 linhas.

with camera_bounds as (
    select
        min(seen_at) as first_camera_event_at
    from {{ ref('fct_camera_events') }}
)

select
    e.evidence_id,
    e.suspect_id,
    e.location_id,
    e.collected_at,
    cb.first_camera_event_at
from {{ ref('fct_evidence') }} e
cross join camera_bounds cb
where e.collected_at is null
   or e.collected_at < cb.first_camera_event_at
   or e.collected_at > date_trunc('day', cb.first_camera_event_at) + interval '42 hours'

