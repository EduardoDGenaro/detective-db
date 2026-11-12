select vitima_id as registro
from {{ ref('laudo_vitima') }}
where inicio_morte is null or fim_morte is null or inicio_morte > fim_morte
union all
select pessoa_id
from {{ ref('testemunhas') }}
where entrada_registrada is null or saida_registrada is null
   or entrada_registrada > saida_registrada
   or inicio_trabalho > fim_trabalho
   or horario_relato > horario_depoimento
union all
select local_id
from {{ ref('locais') }}
where inicio_registro > fim_registro or pessoas_presentes < 0
