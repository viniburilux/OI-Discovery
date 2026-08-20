# TraceFoundry — posicionamento

## Uma frase

**TraceFoundry é a camada de evidência para decisões de discovery que não podem depender de uma lista de links, de um ranking opaco ou de uma resposta de RAG sem proveniência.**

## Para quem é

TraceFoundry foi desenhado para equipes de R&D, technology intelligence, due diligence, scouting científico, inovação corporativa, pesquisa aplicada e operações de conhecimento que precisam decidir **o que investigar a seguir** antes de comprar dados, iniciar uma análise, contratar um parceiro ou comprometer meses de engenharia.

## O problema comercial

Em ambientes técnicos, a pergunta mais cara geralmente aparece antes da análise: qual fonte merece ser aberta, qual registro é realmente o mesmo ativo, qual paper está ligado a qual dataset, qual patente é relevante, qual resultado é apenas um candidato e qual caminho deve ser abandonado?

A busca convencional otimiza descoberta de links. O RAG convencional otimiza geração de respostas sobre um corpus. TraceFoundry otimiza uma etapa anterior e mais operacional: **tornar o espaço de decisão inspecionável**.

## O que o produto faz

TraceFoundry coleta metadata de fontes públicas, normaliza identificadores e campos, aplica restrições explícitas, seleciona candidatos de forma determinística e registra a proveniência de cada resultado. Quando não há evidência suficiente, o sistema pode dizer isso. Quando uma fonte está bloqueada por rate limit ou credencial, isso aparece como bloqueio de dependência, não como ausência de evidência.

## O que o produto não promete

TraceFoundry não declara que um dataset é cientificamente adequado, não interpreta dados brutos, não substitui revisão de domínio, não inventa relações entre papers e ativos e não transforma uma correlação exploratória em conclusão causal. Essa fronteira é parte do valor do produto: ela reduz decisões erradas produzidas por excesso de confiança.

## Casos de uso iniciais

| Contexto | Decisão que TraceFoundry ajuda a preparar |
|---|---|
| Scouting científico | Quais datasets, papers e grupos merecem revisão humana primeiro? |
| Due diligence técnica | O candidato possui metadata, versão, licença e proveniência suficientes para avançar? |
| Patentes e technology intelligence | Quais famílias, classificações e assignees aparecem em uma busca reproduzível? |
| Clean tech e sustentabilidade | Quais fontes públicas sustentam uma hipótese de tecnologia, material ou processo? |
| Pesquisa operacional | O caminho foi explorado, o que foi rejeitado e por que a próxima ação ainda faz sentido? |

## O diferencial defensável

O diferencial não é “usar IA para buscar”. O diferencial é combinar quatro propriedades que normalmente ficam separadas:

1. **Cross-source:** fontes diferentes podem ser consultadas sob contratos canônicos.
2. **Explainable:** seleção e rejeição possuem motivos explícitos.
3. **Epistemic:** candidato operacional, ausência, insuficiência e bloqueio não são tratados como a mesma coisa.
4. **Reproducible:** query, timestamp, metadata observada e decisão são empacotados em manifest versionado.

A camada futura de inteligência poderá usar esses manifests para manter estado de investigação, relacionar claims a evidências e recomendar Research Moves. Essa evolução ainda deve ser validada por experimentos de utilidade; não é uma capacidade declarada do core atual.

## Por que agora

A quantidade de informação técnica cresce mais rápido que a capacidade das equipes de verificar contexto, identidade, licença, versão e adequação antes de agir. O resultado é retrabalho: pesquisadores abrem fontes erradas, engenheiros integram artefatos incompatíveis e equipes de inovação apresentam hipóteses sem trilha de evidência.

TraceFoundry oferece uma fundação pequena, aberta e extensível para colocar ordem nessa etapa sem forçar uma plataforma monolítica.

## Mensagem para parceiros

> **Bring a difficult discovery question. Leave with a reviewable evidence map, explicit gaps and a next action you can defend.**

## Maturidade

O core público está em estágio de **infraestrutura funcional e demonstrável**. Os adapters, contratos, manifests, seleção e testes metadata-only existem. A eficácia comercial — tempo economizado, qualidade superior da decisão ou disposição a pagar — ainda é uma hipótese a ser medida com Value Tests controlados.

Essa distinção é deliberada. TraceFoundry pretende ser confiável antes de ser grandioso.
