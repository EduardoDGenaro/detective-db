-- Modelo staging: padronizacao das evidencias periciais coletadas.
-- Regra explicita para dados incompletos: evidencias sem `suspect_id` identificado
-- sao preservadas com `suspect_id = NULL` e sinalizadas por `is_suspect_identified = FALSE`
-- para analise pericial de vestigios orfaos, sem exclusao silenciosa.
-- Nao aplica DISTINCT para nao mascarar duplicidades da camada raw nos testes.

with source_data as (
    select * from {{ source('raw', 'evidence') }}
),

standardized as (
    select
        trim(cast(evidence_id as varchar)) as evidence_id,
        nullif(trim(cast(suspect_id as varchar)), '') as suspect_id,
        trim(cast(location_id as varchar)) as location_id,
        upper(trim(cast(evidence_type as varchar))) as evidence_type,
        trim(cast(evidence_description as varchar)) as evidence_description,
        cast(collected_at as timestamp) as collected_at,
        upper(trim(cast(status as varchar))) as status,
        case
            when nullif(trim(cast(suspect_id as varchar)), '') is not null then true
            else false
        end as is_suspect_identified
    from source_data
)

select * from standardized

