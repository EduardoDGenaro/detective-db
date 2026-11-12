-- Modelo analitico consolidado do Caso 001 (O Relogio Parado).
-- Agrega evidencias, depoimentos e eventos de camera separadamente por `suspect_id`
-- antes do JOIN final para impedir multiplicacao de contagens (fan-out).
--
-- Formula heuristica centralizada e auditavel:
--   suspicion_score =
--       2 * evidence_count
--     + 3 * inconsistent_testimony_count
--     + 2 * suspicious_location_events
--     + 4 * alibi_camera_conflict_count
--
-- Aviso metodologico: `suspicion_score` e uma heuristica de priorizacao investigativa,
-- nunca uma probabilidade estatistica de culpa ou veredito judicial.

with suspects as (
    select * from {{ ref('dim_suspects') }}
),

evidence_agg as (
    select
        suspect_id,
        count(*) as evidence_count,
        count(case when is_active_evidence then 1 end) as active_evidence_count,
        count(case when not is_active_evidence then 1 end) as discarded_evidence_count
    from {{ ref('fct_evidence') }}
    where suspect_id is not null
    group by suspect_id
),

testimonies_agg as (
    select
        suspect_id,
        count(*) as testimony_count,
        count(case when not consistency_flag then 1 end) as inconsistent_testimony_count,
        cast(coalesce(sum(conflicting_camera_count), 0) as bigint) as alibi_camera_conflict_count
    from {{ ref('fct_testimonies') }}
    group by suspect_id
),

camera_agg as (
    select
        suspect_id,
        count(*) as camera_events_count,
        count(case when is_suspicious_location_event then 1 end) as suspicious_location_events
    from {{ ref('fct_camera_events') }}
    group by suspect_id
),

consolidated as (
    select
        s.suspect_id,
        s.suspect_name,
        s.age,
        s.occupation,
        s.alibi,
        s.risk_level,
        coalesce(e.evidence_count, 0) as evidence_count,
        coalesce(e.active_evidence_count, 0) as active_evidence_count,
        coalesce(e.discarded_evidence_count, 0) as discarded_evidence_count,
        coalesce(t.testimony_count, 0) as testimony_count,
        coalesce(c.camera_events_count, 0) as camera_events_count,
        coalesce(c.suspicious_location_events, 0) as suspicious_location_events,
        coalesce(t.inconsistent_testimony_count, 0) as inconsistent_testimony_count,
        coalesce(t.alibi_camera_conflict_count, 0) as alibi_camera_conflict_count,
        case
            when coalesce(t.inconsistent_testimony_count, 0) > 0
              or coalesce(t.alibi_camera_conflict_count, 0) > 0
            then true
            else false
        end as contradiction_flag,
        (
            2 * coalesce(e.evidence_count, 0)
            + 3 * coalesce(t.inconsistent_testimony_count, 0)
            + 2 * coalesce(c.suspicious_location_events, 0)
            + 4 * coalesce(t.alibi_camera_conflict_count, 0)
        ) as suspicion_score
    from suspects s
    left join evidence_agg e
        on s.suspect_id = e.suspect_id
    left join testimonies_agg t
        on s.suspect_id = t.suspect_id
    left join camera_agg c
        on s.suspect_id = c.suspect_id
)

select
    suspect_id,
    suspect_name,
    age,
    occupation,
    alibi,
    risk_level,
    evidence_count,
    active_evidence_count,
    discarded_evidence_count,
    testimony_count,
    camera_events_count,
    suspicious_location_events,
    inconsistent_testimony_count,
    alibi_camera_conflict_count,
    contradiction_flag,
    suspicion_score,
    dense_rank() over (
        order by suspicion_score desc, alibi_camera_conflict_count desc, suspect_id asc
    ) as investigation_priority_rank,
    (
        '2x Evidencias (' || cast(evidence_count as varchar) || ') + '
        || '3x Depoimentos Inconsistentes (' || cast(inconsistent_testimony_count as varchar) || ') + '
        || '2x Locais Restritos (' || cast(suspicious_location_events as varchar) || ') + '
        || '4x Conflitos Alibi/Camera (' || cast(alibi_camera_conflict_count as varchar) || ') = '
        || cast(suspicion_score as varchar) || ' pts (Heuristica exploratoria, nao conclusiva)'
    ) as score_breakdown
from consolidated
