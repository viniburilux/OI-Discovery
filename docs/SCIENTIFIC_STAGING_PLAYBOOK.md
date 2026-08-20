# Scientific Staging Playbook

## Propósito

O **Scientific Staging Playbook** é um protocolo leve para transformar uma pergunta ampla e um corpus fragmentado em uma próxima ação reproduzível. Ele não substitui revisão científica, análise estatística ou julgamento de especialistas. Seu objetivo é impedir que uma investigação salte diretamente de resultados de busca para uma conclusão.

> O artefato central não é a lista de documentos. É a transição auditável entre uma pergunta, o estado atual da evidência e a próxima ação que reduz uma lacuna.

## O ciclo

| Estágio | Pergunta de controle | Artefato |
|---|---|---|
| 1. Frame | Qual decisão ou investigação precisa ser apoiada? | `DiscoveryQuery` |
| 2. Discover | Quais fontes públicas podem conter evidência relevante? | `DatasetRecord` / `AssetRecord` |
| 3. Normalize | O que cada fonte realmente observou? | `EvidenceReference` |
| 4. Audit | O que pode ser dito sem extrapolar? | `Claim` |
| 5. Gap | O que impede uma conclusão mais forte? | `EvidenceGap` |
| 6. Move | Qual ação mínima reduz a lacuna? | `ResearchMove` |
| 7. Gate | O que encerra, bloqueia ou redireciona a investigação? | `stop_criteria` / decisão |
| 8. Record | O que foi feito e como pode ser reproduzido? | manifest, registry e relatório |

## 1. Formular a pergunta operacional

Uma pergunta útil contém um objeto, um critério de relevância, restrições e uma decisão downstream. “Encontrar pesquisas sobre organoides” é amplo demais. “Quais registros públicos merecem revisão humana para investigar eletrofisiologia de organoides humanos, sem baixar dados, e quais metadados faltam para priorizar a revisão?” já define uma tarefa verificável.

A pergunta deve declarar também o que **não** será feito. Em particular, a descoberta metadata-only não deve ser apresentada como validação experimental, e uma referência bibliográfica não deve ser tratada como prova de que um dataset contém a modalidade desejada.

## 2. Descobrir sem apagar a proveniência

Cada fonte deve gerar um registro com identificador, URI, timestamp, adapter, parâmetros e status. Resultados de fontes diferentes não devem ser misturados por título ou similaridade textual sem manter os identificadores originais. Um zero pode significar ausência, incompatibilidade de ontologia, limite da API ou credencial ausente; esses estados são diferentes.

O TraceFoundry usa manifests versionados e um Discovery Registry append-only para preservar essa trilha. O modo padrão é metadata-only: títulos, identificadores, datas, autores, licenças, formatos e URLs podem ser registrados; dados científicos brutos não são baixados automaticamente.

## 3. Transformar resultados em evidência revisável

Uma `EvidenceReference` aponta para uma observação pública, não para uma interpretação. A evidência deve indicar fonte, URI ou record ID e, quando possível, a observação temporal. A linguagem da claim vem depois.

| Classe | Significado | Exemplo de linguagem |
|---|---|---|
| `observed` | O registro ou fonte sustenta diretamente a afirmação no escopo indicado. | “A API retorna 111 assets.” |
| `inferred` | A relação é plausível, mas depende de uma inferência explícita. | “O título sugere relevância para organoides.” |
| `hypothesis` | Proposição ainda não verificada. | “O conjunto pode suportar uma análise comparativa.” |
| `insufficient` | A fonte não fornece evidência suficiente para a afirmação. | “Não é possível confirmar NWB apenas pelo record.” |
| `blocked` | A verificação foi impedida por dependência, credencial ou limite operacional. | “A consulta live foi bloqueada por rate limit.” |
| `rejected` | A afirmação foi testada e não deve ser usada. | “Não chamar o artigo de benchmark universal.” |
| `contradicted` | Há evidência que entra em conflito com a afirmação. | “O título oficial contradiz a classificação inicial.” |

## 4. Explicitar lacunas

Uma lacuna não é uma falha do sistema. É um resultado útil quando impede uma decisão indevidamente forte. Toda lacuna deve indicar a afirmação afetada, sua severidade, qual evidência seria necessária e se existe uma ação segura para obtê-la.

Lacunas comuns incluem ausência de versão publicada, licença incompleta, falta de relação paper–dataset, formato não exposto no nível do record, identidade de entidade não resolvida e falta de labels para uma avaliação preditiva.

## 5. Emitir um Research Move

Um `ResearchMove` é uma próxima ação limitada por objetivo, rationale, evidências de entrada, lacunas, observação esperada e critérios de parada. Ele deve ser menor do que “investigar tudo”. Exemplos:

- revisar os três assets com maior evidência de modalidade e verificar a documentação associada;
- consultar uma segunda fonte para resolver uma identidade de dataset;
- confirmar licença e versão antes de propor aquisição;
- comparar um candidato com um baseline explícito;
- encerrar a linha quando a evidência necessária não existe.

O move não deve esconder aquisição de dados, execução de código ou uso de credencial. Dependências e riscos precisam aparecer no próprio registro.

## 6. Critérios de parada

Uma investigação pode terminar com `resolved`, `insufficient`, `blocked` ou `rejected`. “Não encontrei evidência suficiente” é uma resposta válida. O objetivo não é forçar uma conclusão positiva, mas reduzir o espaço de decisão sem transformar inferência em fato.

## Fronteira de publicação

Este playbook é público porque é método genérico. Perguntas proprietárias, dados derivados, memória operacional, credenciais, decisões pessoais, arquivos NWB/HDF5/pickle e resultados científicos não auditados permanecem fora do pacote público. Uma fixture pública deve usar metadata de fontes abertas ou dados sintéticos claramente marcados como teste de software; nunca deve insinuar que uma fixture prova uma conclusão científica.

## Implementação no TraceFoundry

Os contratos atuais estão em `src/oi_discovery/investigation.py`. Os schemas estão em `schemas/investigation_state.schema.json` e `schemas/research_move.schema.json`. A fixture V001 em `examples/research_move_v0/` mostra o ciclo completo sobre metadata público, com claims e lacunas explícitas.

## Referências

[1]: https://github.com/viniburilux/TraceFoundry/blob/main/docs/INVESTIGATION.md "TraceFoundry — Investigation State e Research Move"
[2]: https://github.com/viniburilux/TraceFoundry/blob/main/docs/ARCHITECTURE.md "TraceFoundry — arquitetura pública"
[3]: https://github.com/viniburilux/TraceFoundry/blob/main/docs/BENCHMARK_V0_RESULTS.md "TraceFoundry — Benchmark v0 e limites observados"
