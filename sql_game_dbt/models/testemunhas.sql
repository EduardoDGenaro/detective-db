select
    pessoa_id, trim(nome) as nome, profissao,
    cast(inicio_trabalho as timestamp) as inicio_trabalho,
    cast(fim_trabalho as timestamp) as fim_trabalho,
    cast(horario_depoimento as timestamp) as horario_depoimento,
    cast(horario_relato as timestamp) as horario_relato,
    local_declarado_id, relato, alibi, local_registrado_id,
    cast(entrada_registrada as timestamp) as entrada_registrada,
    cast(saida_registrada as timestamp) as saida_registrada,
    fonte_registro, cast(numero_calcado as integer) as numero_calcado, tecido_roupa
from {{ ref('raw_testemunhas') }}
