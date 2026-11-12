select
    vitima_id, trim(nome) as nome, local_id,
    cast(inicio_morte as timestamp) as inicio_morte,
    cast(fim_morte as timestamp) as fim_morte,
    causa_morte, instrumento, dinamica,
    cast(numero_calcado_vestigio as integer) as numero_calcado_vestigio,
    fibra_vestigio, observacao_pericial
from {{ ref('raw_laudo_vitima') }}
