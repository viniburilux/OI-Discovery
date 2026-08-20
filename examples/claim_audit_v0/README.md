# Claim Audit v0

Este exemplo mostra como transformar afirmações públicas sobre organoides e computação biológica em registros revisáveis. Ele usa somente fontes primárias públicas e não contém dados científicos brutos, memória privada ou código de terceiros.

O registro inclui claims observadas, rejeitadas e contraditas. A inclusão de uma claim rejeitada não significa endosso: ela existe para preservar o histórico da correção e demonstrar que o sistema não deve apagar uma formulação forte sem explicar por que ela foi rebaixada.

## Executar a validação

A validação estrutural pode ser feita com qualquer validador JSON Schema compatível com Draft 2020-12 usando `schemas/claim_audit.schema.json`.

## O que este exemplo demonstra

- Uma frase pode ser factual dentro de um escopo e inadequada fora dele.
- Disponibilidade de dados, licença e reprodutibilidade são propriedades diferentes.
- Um registro de dataset pode ser relevante sem provar formato, modalidade ou adequação experimental.
- A conclusão correta às vezes é rejeitar a formulação ou pedir uma próxima verificação.

## Fontes usadas

- PubMed, PMID 36228614: https://pubmed.ncbi.nlm.nih.gov/36228614/
- Nature Electronics, Brainoware: https://www.nature.com/articles/s41928-023-01069-w
- DANDI API, dandiset 001603: https://api.dandiarchive.org/api/dandisets/001603/
