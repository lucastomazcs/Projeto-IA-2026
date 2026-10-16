# Precificação Inteligente para Pequenos Vendedores

Prova de Conceito acadêmica para apoiar pequenos vendedores na definição de preços em marketplaces e e-commerce.

## Objetivo

Combinar custos do vendedor, taxas do canal e preços comparáveis para apresentar um preço mínimo viável e uma recomendação explicável. O projeto será desenvolvido para atender ao roteiro da disciplina SIN 323: problema real, IA com papel essencial, PoC demonstrável, validação e análise crítica.

## Estado atual

Em definição. O plano inicial propõe regras de precificação como MVP e deixa modelos de IA para uma fase posterior. Para atender ao requisito acadêmico de IA essencial, a PoC deverá incluir no MVP uma tarefa de IA claramente delimitada — por exemplo, identificar e ranquear anúncios comparáveis a partir de título, marca, modelo e atributos — e avaliar essa tarefa com dados rotulados e uma linha de base simples. O cálculo financeiro continuará determinístico e auditável.

## Estrutura

- `backend/`: API e lógica da PoC.
- `frontend/`: interface demonstrável (a definir).
- `docs/`: requisitos, decisões e avaliação do plano.
- `data/sample/`: dados sintéticos ou com licença de uso documentada.

## Princípios de escopo

- Começar por um único canal e validar o acesso à fonte de dados antes de prometer coleta automática.
- Não usar scraping não autorizado nem contornar bloqueios ou limites.
- Exibir fonte, data, moeda e atributos relevantes dos comparáveis.
- Não recomendar preço abaixo do mínimo viável sem sinalizar inviabilidade.
- Não alegar previsão de demanda ou causalidade sem validação adequada.

## Execução

O protótipo de cálculo inicial está em `backend/pricing.py` e não requer dependências externas.

```bash
python backend/pricing.py
```

## Próximos passos

1. Confirmar o recorte do problema e o público piloto com vendedores.
2. Definir e validar a tarefa de IA de comparação de produtos.
3. Definir os dados permitidos e um protocolo de avaliação.
4. Construir a PoC demonstrável e registrar resultados, limitações e riscos.

## Disciplina

SIN 323 — Inteligência Artificial, Projeto Prático 2026/2. Apresentação prevista no enunciado para 04/12/2026.
