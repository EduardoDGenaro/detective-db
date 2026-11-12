select local_id, trim(nome) as nome, tipo, cast(publico as boolean) as publico,
    movimentacao, acesso, cast(pessoas_presentes as integer) as pessoas_presentes,
    cast(inicio_registro as timestamp) as inicio_registro,
    cast(fim_registro as timestamp) as fim_registro
from {{ ref('raw_locais') }}
