# Avaliação do plano em relação ao enunciado

## Instruções do enunciado (Projeto.pdf)

O documento da disciplina define os requisitos avaliáveis: problema real relevante; IA necessária, com entradas, saídas e papel explicado; PoC funcional e demonstrável; evidências de validação; análise crítica de limitações, erros, riscos, vieses, privacidade, segurança e supervisão humana quando pertinentes. A entrega inclui pôster, demonstração e código/repositório quando aplicável. Esses são requisitos da disciplina.

## Conteúdo do plano (plano_precificacao_inteligente.pdf)

O plano é uma proposta de solução, não uma instrução da disciplina. Ele sugere como escolhas de produto: pequenos vendedores como público; um marketplace piloto; arquitetura web; regras de preço no MVP; ML numa fase posterior; LLM opcional; e hipóteses de monetização. Esses itens podem ser ajustados para satisfazer o enunciado.

## Aderência

| Requisito da disciplina | O que o plano cobre | Avaliação |
|---|---|---|
| Problema real e relevância | Público e dificuldade de precificar considerando custo e mercado | Bem encaminhado; falta evidência direta das entrevistas propostas. |
| IA essencial | MVP baseado em fórmula e estatísticas; ML fica para fase 2 e LLM é opcional | **Lacuna principal:** do jeito atual, a IA pode ser acessória, contrariando o enunciado. |
| PoC funcional | Fluxo, funcionalidades, stack e critério de sucesso definidos | Bom ponto de partida; ainda precisa ser implementado e demonstrável. |
| Validação | Métricas financeiras, de matching e de utilidade propostas | Alinhado; falta executar e registrar resultados. |
| Análise crítica e uso responsável | Restrições de dados, limites, riscos de custos, comparabilidade e LGPD | Bem encaminhado; detalhar erros do matching, revisão humana e limites de inferência. |
| Pôster e domínio | Não detalha plano de preparação do pôster | Acrescentar síntese visual, resultados e ensaio da demonstração perto da entrega. |

## Ajuste recomendado

A PoC agora coloca o matching no fluxo central: embeddings do Sentence Transformers multilíngue, limiar escolhido em desenvolvimento e verificações técnicas híbridas antes da comparação de preços. A avaliação atual está em [matching_avaliacao.md](matching_avaliacao.md). Próximos passos: ampliar pares negativos, revisar os rótulos com avaliadores e repetir o teste em anúncios de outras fontes. A recomendação financeira continua explícita e não atribui ao modelo previsões de venda ou ganho de margem.

## Sequência inicial sugerida

1. Validar dor, público e fluxo com vendedores.
2. Definir atributos e rótulos para comparabilidade de produtos e obter uma fonte de dados permitida.
3. Implementar baseline de matching e avaliação; documentar limites e revisão humana.
4. Integrar o matching ao cálculo determinístico de preço mínimo e recomendação.
5. Demonstrar um caso completo e apresentar métricas, erros e limitações.

## Nota sobre a fórmula

Para margem definida como percentual do preço de venda, o plano usa `preço mínimo = (custo variável + tarifa fixa) / (1 − taxa percentual − margem-alvo)`. A fórmula exige que taxa e margem somem menos que 100%; o protótipo inicial valida essa condição.
