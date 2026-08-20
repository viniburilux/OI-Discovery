# TraceFoundry — demo orientada a decisão

## A pergunta

Imagine uma equipe que precisa decidir se vale investigar um dataset de eletrofisiologia de organoides humanos. A pergunta não é apenas “encontre resultados”. A pergunta é:

> **Quais candidatos públicos merecem revisão humana antes de qualquer aquisição ou análise?**

## O fluxo

1. A equipe define fonte, dataset, versão, formato, tamanho e requisitos de proveniência.
2. O adapter consulta apenas metadata pública.
3. O core normaliza a resposta em records canônicos.
4. A seleção explica por que cada item entrou ou saiu.
5. O manifest registra o que foi observado, quando foi observado e o que continua desconhecido.
6. Um revisor decide se vale avançar para aquisição controlada.
7. A camada de investigação registra claims, lacunas e a próxima ação justificável.

## Executar localmente

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .

PYTHONPATH=src python scripts/oi_discover.py \
  --source dandi \
  --dataset-id 001603 \
  --version draft \
  --format nwb \
  --max-assets 3 \
  --output demo_manifest.json
```

Abra `demo_manifest.json` e observe especialmente:

- a query normalizada e seu hash;
- a fonte e a versão consultadas;
- os identificadores oficiais e URLs;
- o motivo de seleção ou rejeição;
- os warnings e as limitações;
- `download_performed: false`.

## Da descoberta ao Research Move

Depois da consulta, execute a fixture pública de investigação:

```bash
PYTHONPATH=src python scripts/show_research_move.py
PYTHONPATH=src python tests/run_research_move_tests.py
```

A saída mostra uma pergunta, quatro referências metadata-only, claims com status epistemológico, lacunas abertas e um Research Move com objetivo, ação, justificativa e critérios de parada. A fixture foi construída com URLs públicas do V001 e não contém dados brutos, memória privada ou estado experimental inédito.

## O que a demo prova

A demo prova que o caminho de **query → adapter → records → seleção → manifest → investigation state → Research Move** é representável e reproduzível sob a política metadata-only. Ela não prova que o dataset é adequado à hipótese científica, que os dados possuem qualidade suficiente ou que o resultado gera ganho de produtividade para uma equipe.

## O que uma equipe faria depois

Se o manifest for promissor, um especialista pode revisar os candidatos, confirmar documentação e licença, relacionar papers ou códigos e autorizar uma aquisição controlada no ambiente privado apropriado. Se não houver candidatos, a equipe recebe uma ausência operacional ou um bloqueio explícito, em vez de uma lista artificialmente preenchida.

## Uma segunda demo: patentes

```bash
export PATENTSVIEW_API_KEY="..."
PYTHONPATH=src python scripts/oi_discover.py \
  --source patentsview \
  --dataset-id "methanol detection" \
  --max-assets 5 \
  --output patent_manifest.json
```

PatentsView é usado aqui como fonte de metadata de patentes. O resultado não substitui leitura técnica ou análise jurídica; ele torna a busca reproduzível e preserva IDs, títulos, classificações, inventores, assignees e famílias quando retornados pela API.
