-- Tabela fato de evidencias periciais enriquecida com dimensoes de suspeito e local.
-- Inclui sequenciamento por janela temporal dentro de cada local periciado.

with evidence as (
    select * from {{ ref('stg_evidence') }}
),

suspects as (
    select * from {{ ref('dim_suspects') }}
),

locations as (
    select * from {{ ref('dim_locations') }}
)

select
    e.evidence_id,
    e.suspect_id,
    coalesce(s.suspect_name, 'NAO IDENTIFICADO') as suspect_name,
    e.location_id,
    l.location_name,
    l.area_type,
    l.security_tier,
    l.is_restricted_zone,
    e.evidence_type,
    e.evidence_description,
    e.collected_at,
    e.status,
    e.is_suspect_identified,
    case
        when e.status <> 'DISCARDED' then true
        else false
    end as is_active_evidence,
    row_number() over (
        partition by e.location_id
        order by e.collected_at asc, e.evidence_id asc
    ) as location_collection_seq
from evidence e
left join suspects s
    on e.suspect_id = s.suspect_id
left join locations l
    on e.location_id = l.location_id

