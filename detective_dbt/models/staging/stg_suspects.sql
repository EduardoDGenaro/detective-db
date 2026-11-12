-- Modelo staging: padronizacao cadastral dos suspeitos do Caso 001.
-- Preserva granularidade original da fonte para nao mascarar testes de qualidade.

with source_data as (
    select * from {{ source('raw', 'suspects') }}
),

standardized as (
    select
        trim(cast(suspect_id as varchar)) as suspect_id,
        trim(cast(suspect_name as varchar)) as suspect_name,
        cast(age as integer) as age,
        trim(cast(occupation as varchar)) as occupation,
        trim(cast(alibi as varchar)) as alibi,
        upper(trim(cast(risk_level as varchar))) as risk_level
    from source_data
)

select * from standardized

