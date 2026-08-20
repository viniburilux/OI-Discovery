# Claim Audit Starter Kit

## O que este kit resolve

Pesquisas técnicas falham com frequência não por falta de documentos, mas porque frases fortes são copiadas sem escopo, licença, versão ou fonte primária. Este kit transforma uma afirmação em um objeto revisável: statement, status epistemológico, evidências, escopo, correção e próximo gate.

O kit não é um detector automático de verdade. Ele é uma disciplina para que cada afirmação possa ser contestada, corrigida ou rebaixada sem apagar o histórico.

## Estrutura mínima

Cada claim deve responder a cinco perguntas:

1. **O que exatamente está sendo afirmado?**
2. **Qual fonte primária sustenta a afirmação?**
3. **Qual parte é observação e qual parte é interpretação?**
4. **Qual limitação impede uma formulação mais forte?**
5. **O que acontece se a claim estiver errada?**

## Vocabulário

| Status | Uso correto | Não usar como |
|---|---|---|
| `observed` | A fonte observada sustenta diretamente a frase no escopo declarado. | Prova universal. |
| `inferred` | A frase deriva de uma relação explícita entre observações. | Fato primário. |
| `hypothesis` | A frase é uma proposta para teste. | Resultado. |
| `insufficient` | A fonte é relevante, mas não sustenta a frase. | Ausência universal. |
| `blocked` | A verificação não pôde ser concluída por dependência. | Ausência de evidência. |
| `rejected` | A formulação foi considerada inadequada. | Falha do projeto inteiro. |
| `contradicted` | Uma fonte ou observação conflita com a frase. | Resolução automática do conflito. |

## Processo recomendado

### 1. Capturar a frase sem melhorar sua retórica

Registre a frase original ou a formulação de trabalho. Não substitua “pode indicar” por “demonstra”, e não retire qualificadores que mudam o escopo.

### 2. Localizar a fonte primária

Priorize paper original, repositório oficial, API oficial, registro de dataset ou documentação do mantenedor. Uma página de busca pode ajudar a localizar a fonte, mas não deve ser a única evidência de uma afirmação material.

### 3. Dividir a frase em subclaims

“Dataset aberto, humano, de organoides, com eletrofisiologia e pronto para Colab” contém várias claims independentes. Cada uma precisa de evidência própria. Um título relevante não confirma licença, formato, tamanho, versão nem reprodutibilidade.

### 4. Registrar limitações e correções

Quando a frase estiver exagerada, não basta apagá-la. Registre a formulação corrigida, a evidência que provocou a correção e a consequência operacional. Isso preserva aprendizado e impede que o mesmo erro volte em outro relatório.

### 5. Definir o próximo gate

Uma claim pode ser aceita no escopo atual e ainda exigir uma ação antes de virar decisão. Exemplos: confirmar licença, conferir uma versão publicada, verificar relação paper–dataset, testar uma API ou realizar revisão humana.

## Exemplo de redação disciplinada

> **Formulação forte:** “O conjunto é imediatamente pronto para Colab e permite reproduzir os resultados.”
>
> **Auditoria:** a fonte confirma um registro aberto e arquivos processados, mas a licença, a compatibilidade de execução e o escopo de reprodução precisam ser verificados separadamente.
>
> **Formulação corrigida:** “O registro é um candidato público para um teste controlado; a reprodução integral ainda não foi demonstrada.”

## Regras de publicação

Uma claim auditada pode ser publicada quando suas fontes são públicas, a licença é compatível, a formulação é limitada ao que foi observado, o histórico de correção é preservado e nenhuma credencial, dado privado ou arquivo científico sensível é incorporado.

Claims sobre consciência, inteligência geral, prioridade histórica, “primeiro benchmark”, disponibilidade completa de dados ou reprodução integral exigem revisão adicional e não devem ser inferidas de um único paper, README ou registro.

## Relação com TraceFoundry

O formato complementar `claim_audit.schema.json` pode alimentar `Claim`, `EvidenceReference`, `EvidenceGap` e `ResearchMove`. O Claim Audit Starter Kit é público porque descreve um método genérico; registros ligados a estratégia, memória pessoal, decisões do usuário e dados derivados permanecem privados.

## Referências

[1]: https://github.com/viniburilux/TraceFoundry/blob/main/docs/INVESTIGATION.md "TraceFoundry — estados epistemológicos"
[2]: https://github.com/viniburilux/TraceFoundry/blob/main/docs/TEST_MATRIX.md "TraceFoundry — matriz de testes"
[3]: https://github.com/viniburilux/TraceFoundry/blob/main/CONTRIBUTING.md "TraceFoundry — padrões de contribuição"
