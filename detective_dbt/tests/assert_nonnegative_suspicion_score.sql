-- Teste personalizado: garante que nenhum suspeito possua `suspicion_score` negativo
-- ou nulo na tabela consolidada `mart_case_summary`.
-- No dbt, o teste passa quando a consulta retorna 0 linhas.

select
    suspect_id,
    suspect_name,
    suspicion_score
from {{ ref('mart_case_summary') }}
where suspicion_score is null
   or suspicion_score < 0

