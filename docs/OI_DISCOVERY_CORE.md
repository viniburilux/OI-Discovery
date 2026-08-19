# OI Discovery Core

## Propósito

`OI Discovery Core` é a primeira camada reutilizável do OI Discovery. Ele responde a uma pergunta operacional antes da análise científica:

> **Quais assets públicos de um corpus atendem a uma consulta de formato, tamanho e proveniência, e por que cada asset foi incluído ou rejeitado?**

O módulo é deliberadamente **metadata-first**. Ele consulta metadados públicos, normaliza o resultado para um contrato comum, aplica filtros explicáveis e gera um manifest reproduzível. Não baixa automaticamente dados biológicos, não desserializa pickle e não afirma que um dataset é adequado para qualquer hipótese científica sem revisão humana.

## Arquitetura

```text
DiscoveryQuery
    ↓
DiscoveryAdapter
    ↓
DatasetRecord + AssetRecord
    ↓
EligibilityDecision
    ↓
DiscoveryResult
    ↓
discovery_manifest.json
```

O adapter DANDI é a primeira implementação. A intenção é adicionar OpenAlex, Crossref, Zenodo e GitHub sem mudar o contrato de saída.

## Uso

A partir da raiz do repositório:

```bash
PYTHONPATH=src python scripts/oi_discover.py \
  --source dandi \
  --dataset-id 001603 \
  --version draft \
  --format nwb \
  --max-assets 1 \
  --output data_catalog/discovery_result.json
```

A execução real requer rede e deve ser feita conscientemente pelo usuário ou por um job autorizado. O comando não baixa nenhum asset; o manifest sempre contém `download_performed: false`.

## Contrato de saída

Cada decisão contém:

| Campo | Significado |
|---|---|
| `eligible` | O asset atende aos filtros determinísticos da consulta |
| `score` | Pontuação transparente de aderência aos critérios |
| `reasons` | Critérios satisfeitos |
| `rejected_reasons` | Critérios que causaram rejeição |
| `source_url` / `content_url` | Origem para auditoria e eventual aquisição controlada |
| `raw_metadata` | Resposta de origem preservada para reprocessamento |

O schema público está em `schemas/discovery_manifest.schema.json`.

## O que pode crescer a partir daqui

O próximo adapter deve ser escolhido por utilidade e não por quantidade de APIs. A ordem recomendada é adicionar uma camada de normalização semântica de dataset, depois um catálogo local de manifests e, só então, uma interface de busca. A descoberta de dados deve permanecer separada da execução de análises para que um resultado negativo de um experimento não corrompa a proveniência do corpus.

## Limites epistemológicos

Um asset elegível é apenas um **candidato operacional**. Elegibilidade não significa qualidade biológica, adequação estatística, compatibilidade experimental ou validade para uma hipótese. Essas propriedades exigem camadas posteriores de avaliação e, quando necessário, inspeção humana do paper, licença, estrutura do arquivo e desenho experimental.

## Licenciamento e publicação

Os adapters devem respeitar a licença e os termos da fonte. O repositório deve versionar código próprio, schemas, manifests pequenos e documentação; dados brutos, arquivos NWB/HDF5 grandes, pickles e credenciais permanecem fora do histórico Git conforme `docs/download_policy.md`.

## Ligação com o LuxMemory

Um manifest pode ser transformado em um link revisável sem escrever diretamente no banco de memória:

```bash
PYTHONPATH=src python scripts/link_manifest_to_luxmemory.py \
  --manifest data_catalog/discovery_result.json \
  --output data_catalog/discovery_memory_link.json \
  --memory-type result \
  --capability-id CAP-OBS-EVIDENCE_MEMORY_DECISION
```

O link preserva o hash da consulta, observações de metadados por asset, status `candidate`, limitações e IDs de capacidades/gates fornecidos explicitamente. O link não afirma adequação científica e deve passar por revisão antes de ingestão no LuxMemory.

## Exemplo real, metadata-only

`examples/dandi_001603_memory_link.json` foi gerado offline a partir do manifest DANDI já versionado em `experiments/001_outputs/dandi_001603_manifest.json`. O resultado aponta para um único asset selecionado, preserva o hash da consulta e mantém o status `candidate`; ele não contém o NWB bruto e não representa uma conclusão sobre adequação científica.
