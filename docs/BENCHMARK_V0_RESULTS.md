# OI Discovery — Benchmark v0: resultados reproduzíveis

**Data da execução:** 19 de agosto de 2026. **Política:** metadata-only; nenhum dataset, PDF, claim completo ou arquivo científico foi baixado. **Revisão humana:** obrigatória antes de qualquer conclusão científica, jurídica, de licenciamento ou de produto.

## Síntese executiva

O Benchmark v0 foi executado como um teste da capacidade operacional do OI Discovery de transformar perguntas heterogêneas em consultas reproduzíveis, manifests versionados, seleção explicável e decisões conservadoras. Foram registradas **18 entradas** no registry append-only: **16 casos executados ou bloqueados** distribuídos entre oito perguntas e **duas perguntas pendentes** por ausência de módulos públicos necessários.

O resultado mais importante não é a quantidade de candidatos selecionados. Em vários casos, o pipeline encontrou registros operacionais, mas classificou a resposta como **`insufficient_evidence`** porque os adapters ainda não normalizam todas as restrições da pergunta. Isso é comportamento deliberado: uma lista de resultados relevantes por texto não é tratada como prova de humanidade do sistema, modalidade eletrofisiológica, condição de baixa temperatura, licença, documentação, equivalência NWB, família de patente ou prontidão científica.

| Categoria de resultado | Quantidade | Interpretação |
|---|---:|---|
| Casos com manifest e avaliação conservadora | 12 | Há registros metadata-only, mas pelo menos uma restrição relevante permanece não resolvida. |
| Casos bloqueados por dependência | 4 | O resultado não representa ausência de evidência; representa falta de chave ou rate limit da fonte. |
| Perguntas pendentes por módulo | 2 | B006 requer ligação paper-to-code; B010 requer mapa cross-source e gate de conflitos. |
| Downloads científicos | 0 | A política metadata-only foi preservada em todos os casos. |

Os artefatos primários são o [resumo JSON do benchmark](../benchmark/results_v0.json), o [registry append-only](../benchmark/registry_v0.jsonl) e os [manifests individuais](../benchmark/runs_v0/). O comando de execução foi [`scripts/run_benchmark_v0.py`](../scripts/run_benchmark_v0.py).

## Matriz de cobertura por pergunta

| ID | Pergunta / domínio | Cobertura executada | Resultado observado | Próximo gate |
|---|---|---|---|---|
| **B001** | Organoides humanos, eletrofisiologia e NWB | DANDI, Zenodo e OpenAlex; três manifests | **Insufficient evidence.** Foram selecionados candidatos operacionais, mas humanidade, modalidade e suporte NWB não são filtros normalizados em todos os adapters. | Revisar metadata de fonte e criar campos canônicos para sistema biológico, modalidade e documentação/NWB. |
| **B002** | Recuperação de lítio com restrição de baixa temperatura | OpenAlex; um manifest com 25 registros e 3 candidatos | **Insufficient evidence.** A condição de temperatura exige inspeção de abstract/full text; Crossref ainda não está disponível. | Implementar extração de condições de processo e adapter Crossref antes da comparação técnica. |
| **B003** | Manguezais no Brasil com licença/access status | Zenodo e OpenAlex; dois manifests com 25 registros e 3 candidatos por fonte | **Insufficient evidence.** A relevância geográfica e completude de licença/access ainda exigem revisão; paper não prova dataset acessível. | Normalizar licença, access status e evidência geográfica; adicionar controle de duplicatas. |
| **B004** | Recuperação de minerais/metais para triagem de rotas | OpenAlex executado; PatentsView bloqueado | **Insufficient evidence** no caso OpenAlex; **dependency blocked** no caso de patente por ausência de `PATENTSVIEW_API_KEY`. | Reexecutar PatentsView com credencial e implementar comparação paper-patente por material, método e identificadores. |
| **B005** | Famílias de patentes sobre detecção de metanol | PatentsView não consultado | **Dependency blocked**, não ausência de patentes: a chave `PATENTSVIEW_API_KEY` não estava disponível e nenhuma chamada de rede foi tentada. | Executar o smoke test metadata-only com chave; depois validar família, prioridade, jurisdição, claims e estado legal manualmente. |
| **B006** | Código associado a papers e instruções de reprodução | Não executado | **Pending adapter.** O núcleo público ainda não tem adapter GitHub/Crossref para evidência paper-to-code. | Implementar ligação de proveniência entre paper, repositório, licença e instruções de reprodução. |
| **B007** | Comparação Zenodo/OpenAlex e duplicatas | Zenodo executado; OpenAlex bloqueado por HTTP 429 | Zenodo produziu 25 registros e 3 candidatos, mas a conclusão foi **insufficient evidence** porque o módulo de deduplicação cross-source não existe. OpenAlex foi registrado como **dependency blocked**, não como ausência. | Adicionar retry/backoff e identificação de DOI/título/autoria/ano; produzir decisão conservadora de merge. |
| **B008** | Acessibilidade, licença e documentação suficientes para próxima etapa | DANDI e Zenodo executados; PatentsView bloqueado | **Insufficient evidence** nos datasets; **dependency blocked** na fonte de patentes. A camada atual não implementa um readiness gate completo. | Normalizar access, licença e documentação e publicar uma matriz de prontidão separada de relevância científica. |
| **B009** | NWB, eletrofisiologia, sistema humano, máximo de 1 MiB e documentação | DANDI e Zenodo executados; dois manifests | **Insufficient evidence** com **zero candidatos selecionados** em ambas as fontes. DANDI rejeitou 111/111 por `above_max_size`; Zenodo rejeitou 25/25 por formato e/ou tamanho. Esta é a resposta negativa explícita esperada pelo controle. | Manter a ausência como resultado válido; somente relaxar restrições mediante decisão explícita e nova consulta versionada. |
| **B010** | Evidências em papers, datasets e patentes para produção sustentável | Não executado | **Pending cross-source module.** O núcleo ainda não produz um mapa único de evidências, conflitos e readiness gate entre tipos de fonte. | Implementar merge com proveniência preservada, conflitos visíveis e decisão explorar/validar/construir/parar. |

## Fatos observados, inferências e hipóteses

### Fatos observados

O teste offline passou com a mensagem `offline_tests_ok: patent adapter, selection, manifest, bridge, legacy manifest, schema`. O `PatentAdapter.normalize_response()` converteu uma fixture contendo identificadores, títulos, datas, inventores, assignees, classificação, prioridade e família em `DatasetRecord` e `AssetRecord`, mantendo `content_url=None`. O smoke test cross-domain também passou para DANDI, Zenodo e OpenAlex, com 111, 25 e 25 registros respectivamente nas consultas já estabelecidas, sempre com `download_performed=false`.

A execução do benchmark gerou manifests para os casos com resposta de fonte e entradas explícitas para bloqueios. No controle B009, a restrição de tamanho não foi relaxada: DANDI rejeitou todos os 111 assets por `above_max_size`, enquanto Zenodo rejeitou todos os 25 por formato não solicitado e/ou tamanho. Portanto, o sistema não fabricou um candidato para satisfazer a pergunta.

### Inferências sustentadas

A arquitetura é estruturalmente reutilizável além de organoides porque o mesmo caminho — adapter, contrato canônico, seleção, manifest, avaliação e registry — foi aplicado a fontes de datasets, registros de repositório, literatura e, offline, patentes. Essa é uma inferência sobre **generalização estrutural**, não sobre precisão, valor científico ou maturidade comercial.

O benchmark também mostra que o sistema já consegue separar quatro estados operacionalmente diferentes: candidato metadata-only que ainda exige revisão, insuficiência explícita, bloqueio por dependência externa e pergunta pendente por ausência de módulo. Essa separação é mais informativa do que tratar todo resultado vazio como “não existe”.

### Hipóteses ainda não validadas

Ainda não foi medido se a seleção explicável economiza tempo ou melhora decisões de pesquisadores em comparação com busca manual, API bruta ou RAG convencional. Também não há gold labels de especialistas, teste de recall, avaliação de deduplicação ou estudo de qualidade da próxima ação. Os campos `selected` nos manifests são **candidatos operacionais**, não uma classificação de relevância científica.

## Limitações técnicas reveladas

A seleção comum atualmente opera sobre formato, modalidade, tamanho e presença de URL de fonte. Ela não impõe, de forma geral, licenciamento, access status, documentação, sistema humano, condições de processo, família de patente, jurisdição, estado legal, claims ou deduplicação cross-source. Por isso, essas condições foram registradas como `hard_constraints` e `unresolved_constraints` na avaliação, sem serem silenciosamente convertidas em filtros textuais.

O OpenAlex respondeu HTTP 429 durante a consulta de B007. O runner passou a capturar esse evento como `dependency_blocked` com a URL e a ação de retry, em vez de classificá-lo como ausência de literatura. PatentsView foi bloqueado pela ausência de `PATENTSVIEW_API_KEY`; nenhuma credencial foi inventada, nenhum valor foi exposto e nenhuma chamada foi executada sem a chave.

## Artefatos e reprodução

A execução pode ser reproduzida a partir da raiz do repositório com:

```bash
python3 -m py_compile $(find src scripts tests -name '*.py' -print)
PYTHONPATH=src python3 tests/validate_benchmark.py
PYTHONPATH=src python3 tests/run_offline_tests.py
PYTHONPATH=src python3 scripts/run_benchmark_v0.py
```

A execução live depende de rede e de disponibilidade das fontes públicas. Para incluir PatentsView, é necessário configurar `PATENTSVIEW_API_KEY`; a ausência da variável deve permanecer como `dependency_blocked` até que o teste seja realmente executado. Nenhum comando acima deve ser interpretado como autorização para baixar dados científicos.

## Próximas decisões práticas

O Benchmark v0 já é suficiente para **validar a infraestrutura**, não para vender uma promessa de descoberta científica. A prioridade recomendada é implementar o readiness/deduplication gate e adicionar o adapter Crossref/GitHub, porque B006, B007, B008 e B010 dependem dessas capacidades. Em paralelo, uma execução PatentsView com chave autorizada deve completar B004/B005/B008 e testar a hipótese de que famílias e prioridade podem ser usadas para reduzir duplicação documental.

Depois desses gates, o próximo experimento de valor deve ser humano e pequeno: selecionar cinco perguntas reais, pedir a um pesquisador que avalie candidatos, rejeições, proveniência e próxima ação, e registrar correções. Esse teste deve medir **tempo para decisão e qualidade da próxima etapa**, não apenas número de resultados.

## Referências

[1] [OI-Discovery — repositório público](https://github.com/viniburilux/OI-Discovery) — implementação, contratos, adapters e testes.

[2] [DANDI API](https://api.dandiarchive.org/api/) — fonte pública de metadata de dandisets e assets.

[3] [Zenodo Records API](https://developers.zenodo.org/) — fonte pública de metadata de records.

[4] [OpenAlex API](https://docs.openalex.org/) — fonte pública de metadata bibliográfica.

[5] [PatentsView Search API](https://search.patentsview.org/docs/docs/Search%20API/SearchAPIReference/) — fonte pública de metadata de patentes; chamadas live exigem chave.

[6] [LuxMemory](https://github.com/viniburilux/LuxMemory) — camada privada de memória estruturada conectada pela ponte revisável.
