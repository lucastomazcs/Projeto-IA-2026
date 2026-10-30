# Precificação Inteligente para Pequenos Vendedores

Prova de Conceito acadêmica para apoiar pequenos vendedores na definição de preços em marketplaces e e-commerce.

## Objetivo

Combinar custos do vendedor, taxas do canal e preços comparáveis para apresentar um preço mínimo viável e uma recomendação explicável. O projeto será desenvolvido para atender ao roteiro da disciplina SIN 323: problema real, IA com papel essencial, PoC demonstrável, validação e análise crítica.

## Estado atual

`streamlit_app.py` agora reúne a apresentação do Precifica, o formulário e os resultados na mesma tela. Ao clicar em **Prever preço**, a aplicação calcula e atualiza as métricas e gráficos logo abaixo do formulário. A landing page HTML em `frontend/` permanece como entrada visual opcional. Os anúncios ainda são fictícios; banco de dados e modelo de IA serão integrados depois.

Para atender ao requisito acadêmico de IA essencial, a PoC deverá incluir uma tarefa de IA claramente delimitada — identificar e ranquear anúncios comparáveis a partir de título, marca, modelo e atributos — e avaliar essa tarefa com dados rotulados e uma linha de base simples. O cálculo financeiro continuará determinístico e auditável.

## Estrutura

- `backend/`: API e lógica da PoC.
- `frontend/`: protótipo responsivo em HTML, CSS e JavaScript, com apresentação e tela de precificação.
- `streamlit_app.py`: formulário Python, métricas e gráficos Plotly.
- `tests/`: testes financeiros, de parâmetros, do handoff e da aplicação Streamlit.
- `docs/`: requisitos, decisões e avaliação do plano.
- `data/sample/`: dados sintéticos ou com licença de uso documentada.

## Princípios de escopo

- Começar por um único canal e validar o acesso à fonte de dados antes de prometer coleta automática.
- Não usar scraping não autorizado nem contornar bloqueios ou limites.
- Exibir fonte, data, moeda e atributos relevantes dos comparáveis.
- Não recomendar preço abaixo do mínimo viável sem sinalizar inviabilidade.
- Não alegar previsão de demanda ou causalidade sem validação adequada.

## Execução

### Frontend

Instale as dependências e inicie o Streamlit (Python 3.10+):

```bash
python -m pip install -r requirements.txt
python -m streamlit run streamlit_app.py
```

O Streamlit pode ser acessado diretamente em `http://localhost:8501`.

Na tela do Streamlit, preencha o produto e os custos e clique em **Prever preço**. Métricas e gráficos aparecem na mesma página, abaixo do formulário. Para abrir também a landing page, inicie o servidor opcional `node frontend/serve.cjs`.

Para servir via HTTP, com Node.js e sem instalar dependências:

```bash
node frontend/serve.cjs
```

Acesse `http://127.0.0.1:4173`. Guia completo de execução, publicação e limites em [docs/streamlit.md](docs/streamlit.md).

### Backend inicial

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
