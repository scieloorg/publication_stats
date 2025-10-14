# Comando para Atualizar Dados da Coleção México

## Problema
Os filtros de "ano de publicação" na Coleção México (Analytics) estão mostrando valores incorretos (2250, 2026, 2027, etc.). Esses valores já foram corrigidos no ArticleMeta, mas o índice do ElasticSearch do PublicationStats precisa ser atualizado.

## Solução
Executar o script `publicationstats_loaddata` com os seguintes parâmetros:

### Comando Completo

```bash
publicationstats_loaddata --collection mex --doc_type article --differential
```

### Explicação dos Parâmetros

- `--collection mex` (ou `-c mex`): Especifica a coleção México
- `--doc_type article` (ou `-t article`): Indica que os artigos devem ser atualizados
- `--differential` (ou `-x`): Modo diferencial - compara IDs do ArticleMeta com o índice do PublicationStats e atualiza apenas as diferenças

### Comando Alternativo (com remoção de documentos obsoletos)

Se também for necessário remover documentos que não existem mais no ArticleMeta:

```bash
publicationstats_loaddata --collection mex --doc_type article --differential --delete
```

O parâmetro `--delete` (ou `-d`) remove documentos que estão no índice mas não existem mais no ArticleMeta.

### Comando com Logging Detalhado

Para execução com log detalhado (recomendado para acompanhamento):

```bash
publicationstats_loaddata --collection mex --doc_type article --differential --logging_level INFO
```

### Notas Importantes

1. O comando deve ser executado no servidor onde a aplicação PublicationStats está instalada
2. O modo diferencial (`--differential`) é mais eficiente pois atualiza apenas os documentos que foram modificados
3. O processamento pode levar alguns minutos dependendo da quantidade de artigos na coleção
4. Certifique-se de que as variáveis de ambiente estão configuradas corretamente:
   - `ELASTICSEARCH`: endereço do servidor ElasticSearch
   - `ARTICLEMETA_THRIFTSERVER`: endereço do servidor ArticleMeta Thrift

### Artigos Específicos Mencionados no Issue

Os seguintes artigos foram mencionados como tendo anos incorretos (antes da correção no ArticleMeta):

- Tecnología y ciências del agua v12n1 - Antes: 2026
- Tecnología y ciências del agua v12n2 - Antes: 2026  
- Tecnología y ciências del agua v12n3 - Antes: 2026
- Acta médica Grupo Ángeles v21n4 - Antes: 2027
- Investigación en educación médica v13n50 - Antes: 2250

Após a execução do comando, esses artigos devem aparecer com seus anos corretos nos filtros do Analytics.

## Verificação

Após a execução:

1. Acesse https://analytics.scielo.org/?journal=2007-5057&collection=mex
2. Verifique se o intervalo de datas no filtro "Publishing year" está correto
3. Confirme que não há mais anos futuros incorretos (como 2250)
