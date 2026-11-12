-- Dimensao de suspeitos do Caso 001 (O Relogio Parado).
-- O campo `risk_level` representa apenas a triagem preliminar informada na abertura
-- do caso e nao constitui prova ou conclusao investigativa.

with suspects as (
    select * from {{ ref('stg_suspects') }}
)

select
    suspect_id,
    suspect_name,
    age,
    occupation,
    alibi,
    risk_level,
    case
        when risk_level = 'HIGH' then 1
        when risk_level = 'MEDIUM' then 2
        else 3
    end as risk_priority_order
from suspects

