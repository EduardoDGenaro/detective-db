-- Tabela fato de depoimentos com deteccao estruturada de conflitos de alibi.
-- Regra de contradicao de alibi (MVP): compara `claimed_event_time` e
-- `claimed_location_id` de cada depoimento com `seen_at` e `location_id` das cameras
-- do mesmo suspeito. Sinaliza conflito se houver avistamento em local distinto
-- dentro de uma janela de ate 5 minutos (inclusive).
-- Observacao: trata-se de possivel contradicao sujeita a imprecisoes de relogio ou identificacao.

with testimonies as (
    select * from {{ ref('stg_testimonies') }}
),

suspects as (
    select * from {{ ref('dim_suspects') }}
),

locations as (
    select * from {{ ref('dim_locations') }}
),

camera_events as (
    select * from {{ ref('fct_camera_events') }}
),

alibi_camera_matches as (
    select
        t.testimony_id,
        c.camera_event_id,
        c.camera_label,
        c.location_id as observed_location_id,
        c.location_name as observed_location_name,
        c.seen_at as observed_seen_at,
        abs(date_diff('minute', t.claimed_event_time, c.seen_at)) as time_diff_minutes,
        case
            when c.location_id <> t.claimed_location_id then true
            else false
        end as is_location_mismatch
    from testimonies t
    inner join camera_events c
        on t.suspect_id = c.suspect_id
       and abs(date_diff('minute', t.claimed_event_time, c.seen_at)) <= 5
),

conflict_summary_by_testimony as (
    select
        testimony_id,
        count(case when is_location_mismatch then 1 end) as conflicting_camera_count,
        count(case when not is_location_mismatch then 1 end) as confirming_camera_count,
        string_agg(
            case when is_location_mismatch then camera_event_id || ' (' || camera_label || ')' end,
            ', '
            order by observed_seen_at asc
        ) as conflicting_camera_refs,
        string_agg(
            case when is_location_mismatch then observed_location_name end,
            ', '
            order by observed_seen_at asc
        ) as conflicting_observed_locations,
        min(case when is_location_mismatch then observed_seen_at end) as closest_conflict_seen_at,
        min(case when is_location_mismatch then time_diff_minutes end) as min_conflict_diff_minutes
    from alibi_camera_matches
    group by testimony_id
)

select
    t.testimony_id,
    t.suspect_id,
    s.suspect_name,
    t.statement,
    t.statement_time,
    t.claimed_location_id,
    l.location_name as claimed_location_name,
    t.claimed_event_time,
    t.consistency_flag,
    coalesce(cs.conflicting_camera_count, 0) as conflicting_camera_count,
    coalesce(cs.confirming_camera_count, 0) as confirming_camera_count,
    case
        when coalesce(cs.conflicting_camera_count, 0) > 0 then true
        else false
    end as has_alibi_camera_conflict,
    cs.conflicting_camera_refs,
    cs.conflicting_observed_locations,
    cs.closest_conflict_seen_at,
    cs.min_conflict_diff_minutes,
    case
        when coalesce(cs.conflicting_camera_count, 0) > 0 then
            'CONFLITO DE ALIBI (JANELA <= 5 MIN): Declarou estar em '
            || coalesce(l.location_name, t.claimed_location_id)
            || ' as '
            || strftime(t.claimed_event_time, '%H:%M')
            || ', mas foi registrado em '
            || coalesce(cs.conflicting_observed_locations, 'outro local')
            || ' pela camera '
            || coalesce(cs.conflicting_camera_refs, 'N/A')
            || ' (diferenca de '
            || cast(cs.min_conflict_diff_minutes as varchar)
            || ' min).'
        when coalesce(cs.confirming_camera_count, 0) > 0 then
            'ALIBI COMPATIVEL COM CAMERA: Registro visual no mesmo local dentro da janela de 5 min.'
        else
            'SEM REGISTRO DE CAMERA NA JANELA DE 5 MIN: Alibi depende de verificacao complementar.'
    end as conflict_rule_explanation
from testimonies t
left join suspects s
    on t.suspect_id = s.suspect_id
left join locations l
    on t.claimed_location_id = l.location_id
left join conflict_summary_by_testimony cs
    on t.testimony_id = cs.testimony_id

