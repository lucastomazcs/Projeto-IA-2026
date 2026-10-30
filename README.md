# Precificação Inteligente para Pequenos Vendedores

Prova de Conceito acadêmica para apoiar pequenos vendedores na definição de preços em marketplaces e e-commerce.

## Objetivo

Combinar custos do vendedor, taxas do canal e preços comparáveis para apresentar um preço mínimo viável e uma recomendação explicável. O projeto será desenvolvido para atender ao roteiro da disciplina SIN 323: problema real, IA com papel essencial, PoC demonstrável, validação e análise crítica.

## Estado atual

`streamlit_app.py` integra a apresentação comercial original do Precifica, a imagem, o formulário e os resultados em uma única experiência. **Prever preço** consulta os CSVs do catálogo, distingue modelos e atualiza métricas e gráficos abaixo do formulário. Os dados são sintéticos e fazem parte da demonstração.

O backend inclui uma linha de base de matching com TF-IDF de palavras e n-gramas de caracteres, similaridade de cosseno, limiar escolhido na divisão de desenvolvimento e teste separado por produto. A seleção do produto usa também marca, modelo e categoria do catálogo para evitar que modelos próximos sejam confundidos. O cálculo financeiro continua determinístico e auditável. O módulo original exportado do Colab não está neste clone; a implementação atual é uma linha de base reproduzível a partir dos CSVs fornecidos, não uma importação literal daquele notebook.

## Estrutura

- `backend/`: API e lógica da PoC.
- `data/sample/`: 492 anúncios, catálogo com 41 modelos e 3.483 pares rotulados.
- `frontend/`: protótipo responsivo em HTML, CSS e JavaScript, com apresentação e tela de precificação.
- `streamlit_app.py`: formulário Python, métricas e gráficos Plotly.
- `tests/`: testes financeiros, de parâmetros, do handoff e da aplicação Streamlit.
- `docs/`: requisitos, decisões e avaliação do plano.
- `docs/matching_avaliacao.md`: protocolo, limiar e métricas por produto.

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

Na tela do Streamlit, use **Começar agora**, preencha o produto e os custos e clique em **Prever preço**. Métricas e gráficos aparecem na mesma página, abaixo do formulário.

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
2. Substituir ou complementar a linha de base quando o código original do Colab e o modelo Sentence Transformers estiverem disponíveis.
3. Ampliar e balancear os pares de teste antes de tratar as métricas como evidência robusta.
4. Validar o catálogo com anúncios reais obtidos por fonte permitida e registrar limitações e riscos.

## Disciplina

SIN 323 — Inteligência Artificial, Projeto Prático 2026/2. Apresentação prevista no enunciado para 04/12/2026.
