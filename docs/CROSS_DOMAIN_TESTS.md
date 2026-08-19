# OI Discovery — cross-domain metadata-only tests

## Objetivo

Este teste verifica se a mesma sequência operacional funciona fora do caso original de organoides:

```text
pergunta → adapter → registros canônicos → seleção explicável → manifest → link LuxMemory
```

Nenhum arquivo científico foi baixado, nenhum notebook foi executado e nenhum conteúdo bruto foi desserializado.

## Execução

```bash
PYTHONPATH=src python3 tests/run_offline_tests.py
PYTHONPATH=src python3 tests/run_cross_domain_live_tests.py
```

O runner live consulta apenas endpoints públicos de metadata e grava os resultados em `/tmp/oi_discovery_cross_domain/`.

## Resultado observado

| Caso | Fonte | Pergunta | Registros retornados | Selecionados | Download |
|---|---|---|---:|---:|---|
| Organoides | DANDI | dandiset `001603`, assets NWB | 111 | 1 | Não |
| Monitoramento ambiental | Zenodo | `mangrove Brazil` | 25 | 3 | Não |
| Tecnologia | OpenAlex | `lithium recovery technology` | 25 | 3 | Não |

Os três casos produziram manifests e passaram pelo mesmo gate de seleção e pela ponte de revisão do LuxMemory. Isso é evidência de **generalização estrutural do contrato**, não prova de que as respostas sejam cientificamente suficientes ou que o produto tenha valor comercial.

## Interpretação correta

O teste de Zenodo encontrou registros públicos relacionados a manguezais; ele ainda não prova cobertura territorial no Brasil, qualidade geoespacial ou adequação para monitoramento remoto. O teste OpenAlex encontrou papers relacionados à tecnologia de recuperação de lítio; ele **não implementa busca de patentes** e não deve ser descrito como cobertura patentária.

A próxima extensão natural é um `PatentAdapter` com uma fonte pública ou autorizada, seguido da mesma matriz de seleção e provenance. Também seria necessário um avaliador humano para medir precisão, cobertura, duplicação, licenciamento e economia de trabalho em perguntas reais.

## Evidência técnica

- `tests/run_offline_tests.py` valida seleção, manifest, schema, bridge e compatibilidade legada.
- `tests/run_live_metadata_tests.py` valida DANDI live e confirmou `download_performed=False`.
- `tests/run_cross_domain_live_tests.py` executa os três casos acima.
- `src/oi_discovery/adapters/dandi.py`, `openalex.py` e `zenodo.py` implementam o mesmo contrato de adapter.
