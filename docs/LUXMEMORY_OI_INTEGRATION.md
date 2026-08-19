# OI Discovery × LuxMemory

## Tese

OI Discovery e LuxMemory não são dois produtos independentes. Eles ocupam posições diferentes no mesmo ciclo de inteligência:

```text
pergunta externa
    ↓
OI Discovery: encontra e normaliza fontes públicas
    ↓
manifest + evidência de proveniência
    ↓
LuxMemory: registra o que foi observado, tentado, decidido e aprendido
    ↓
capacidade/gate/transferência
    ↓
próxima consulta ou experimento
```

O OI Discovery deve permanecer uma camada de **discovery e preparação de corpus**. O LuxMemory deve permanecer uma camada de **memória operacional e decisão**. A ponte entre os dois deve transportar manifests e evidências, não copiar indiscriminadamente datasets ou conversas.

## O que pode ser reutilizado

| Componente existente | Origem | Reuso no OI Discovery | Regra epistemológica |
|---|---|---|---|
| `operational_memory` | `LuxMemory/conversation-memory/docs/MEMORY_SCHEMA.md` | Representar uma pergunta de discovery, uma decisão de seleção ou um resultado de inspeção | Sem origem, não entra como memória |
| Evidência com chave composta | LuxMemory | Anexar URL, resposta bruta, timestamp, query e trecho de metadado a cada seleção | Citação e interpretação permanecem separadas |
| Oito lentes derivadas | LuxMemory | Classificar uma operação de discovery como transformação, proveniência, artefato, capacidade, decisão ou dependência | Lente é interpretação derivada, não fato de fonte |
| Operadores candidatos | LuxMemory | Detectar recorrências entre adapters e workflows, por exemplo `fonte → manifest → análise` | Só vira operador reutilizável após recorrência e revisão |
| `reusable_skill` | LuxMemory | Registrar procedimentos de uso do adapter, filtros e conversão segura | Skill contém inputs, outputs e limitações |
| `capabilities.jsonl` | LuxMemory | Alimentar gates para decidir se o OI deve apenas catalogar, converter, analisar ou parar | Capacidade não é promessa de produto |
| `transformation_episode` | LuxMemory | Registrar transições `pergunta → corpus → manifest → decisão` | Episódio continua candidato até validação |
| `opportunity_portfolio_v1` | LuxMemory | Priorizar quais adapters e fluxos merecem virar módulos públicos | Oportunidade permanece hipótese |
| Adapter DANDI | OI | Primeiro conector concreto para o contrato `DiscoveryAdapter` | API externa é fonte, não verdade científica |
| Política de download seguro | OI | Guardrail público para impedir download, pickle ou execução implícita | Dados brutos ficam fora do Git |
| Experimento 002/003 | OI | Exemplos de consumidores de manifests e análises posteriores | Resultado experimental tem escopo e métricas explícitos |

## Ponte mínima

O primeiro objeto de integração recomendado é `discovery_memory_link`:

```json
{
  "link_id": "link_dandi_001603_2026_08_19_001",
  "source_type": "oi_discovery_manifest",
  "source_path": "data_catalog/discovery_result.json",
  "source": {
    "adapter": "dandi",
    "dataset_id": "001603",
    "version": "draft",
    "query_hash": "sha256:...",
    "source_url": "https://api.dandiarchive.org/api/dandisets/001603/"
  },
  "observations": [
    {
      "asset_id": "...",
      "claim": "asset matches requested format",
      "evidence_role": "metadata_observation",
      "evidence": {
        "field": "path",
        "quote": "...nwb",
        "source_url": "..."
      }
    }
  ],
  "interpretation": {
    "status": "candidate",
    "decision": "candidate_for_inspection",
    "limitations": ["metadata-only", "no scientific suitability established"]
  },
  "luxmemory": {
    "memory_type": "result",
    "memory_id": "mem_oi_...",
    "capability_ids": [],
    "gate_id": null
  }
}
```

A ponte não deve escrever diretamente no banco principal sem validação. Ela pode primeiro gerar `data/links/discovery_memory_links.jsonl`; depois um ingestador idempotente transforma somente links válidos em registros do LuxMemory.

## Fluxo de uma consulta completa

1. O usuário formula uma pergunta operacional, incluindo alvo, restrição e decisão desejada.
2. OI Discovery consulta uma fonte pública e gera um manifest metadata-only.
3. O selector explica quais assets foram aceitos ou rejeitados.
4. O manifest é registrado como evidência de origem no LuxMemory.
5. O LuxMemory associa capacidades e gates relevantes, por exemplo `public_data_traceability` ou `evidence_memory_decision`.
6. Um consumidor posterior executa análise autorizada sobre uma cópia local adequada; execução científica não acontece automaticamente por causa do manifest.
7. O resultado, inclusive falha ou inconclusão, volta como memória operacional com escopo, evidência e próximo passo.

## O que isso permite construir além do output inicial

A combinação dos projetos habilita uma família de ferramentas, não apenas um catálogo de APIs:

| Produto/capacidade | Pergunta respondida | Maturidade inicial |
|---|---|---|
| **Discovery Registry** | Que fontes públicas existem e quais atendem aos filtros? | Implementável agora |
| **Provenance Ledger** | De onde veio cada asset, query e decisão? | Contratos já definidos |
| **Capability Router** | O que o acervo atual permite fazer com essa fonte? | Hipótese sustentada pelo LuxMemory |
| **Experiment Readiness Gate** | O corpus está pronto para análise ou ainda falta uma condição? | Implementável como regra explícita |
| **Cross-source Comparator** | DANDI, OpenAlex, Zenodo e GitHub apontam para objetos relacionados? | Próximo adapter/normalização |
| **Research Memory** | O que já foi tentado, o que falhou e o que merece retomada? | LuxMemory já possui os primitives |
| **Evidence-to-Decision Brief** | Qual próximo experimento ou decisão é defensável? | Ponte futura com o pipeline de patente |

## Limites

OI Discovery não deve afirmar que uma fonte é “boa”, “científica” ou “adequada” apenas porque possui um formato ou metadado. LuxMemory não deve transformar uma oportunidade, capacidade transferível ou síntese conversacional em fato. Toda ponte deve carregar origem, status, confiança e lacunas.

O resultado pretendido é um sistema que saiba dizer tanto **“encontrei uma fonte candidata”** quanto **“ainda não tenho evidência suficiente para recomendar sua análise”**.
