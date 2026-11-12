-- Dimensao de locais monitorados na Mansao Valmont.
-- Classifica zonas de restricao operacional para apoiar a contabilidade de
-- eventos em locais criticos (Cofre, Subsolo e Portao Leste).

with locations as (
    select * from {{ ref('stg_locations') }}
)

select
    location_id,
    location_name,
    area_type,
    city_zone,
    case
        when location_id in ('L001', 'L004', 'L007') then true
        else false
    end as is_restricted_zone,
    case
        when location_id = 'L001' then 'ZONA_CRITICA_COFRE'
        when location_id in ('L004', 'L007') then 'ACESSO_RESTRITO_SERVICO'
        else 'CIRCULACAO_SOCIAL'
    end as security_tier
from locations

