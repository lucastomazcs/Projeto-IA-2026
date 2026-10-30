# Interface comercial e Streamlit

## Fluxo

`streamlit_app.py` reúne a apresentação, o formulário e os gráficos em uma única página. O fluxo é: formulário → **Prever preço** → métricas e gráficos abaixo do formulário.

O formulário do Streamlit executa a previsão na mesma página e preserva os campos. A landing page HTML em `frontend/index.html` continua disponível como uma entrada visual opcional; o formulário integrado e os resultados ficam juntos na aplicação Streamlit.

Os cálculos e gráficos são executados pelo Streamlit com `backend/pricing.py`. O estado da última análise fica na sessão enquanto o usuário atualiza os campos e prevê novamente.

## Rodar localmente

Requer Python 3.10+ e, para servir a página comercial, Node.js. Na raiz do repositório:

```bash
python -m venv .venv
```

Windows / PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

Linux / macOS:

```bash
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run streamlit_app.py
```

O Streamlit fica em `http://localhost:8501`. Preencha o formulário e selecione **Prever preço**. Resultado, comparação e gráficos são renderizados abaixo do formulário na mesma página. A landing page opcional fica em `http://127.0.0.1:4173`:

```bash
node frontend/serve.cjs
```

Abra `http://127.0.0.1:4173` para a apresentação ou `http://localhost:8501` para o fluxo integrado de previsão.

## Resultados

- Preço mínimo calculado pelos custos, taxa e margem, arredondado para cima ao centavo.
- Sugestão pela mediana dos anúncios, apenas se atender ao mínimo.
- Lucro e margem sobre o preço de venda.
- Comparação dos anúncios com linhas de mínimo e sugestão.
- Gráfico de composição do preço de venda.
- Simulação da variação do mínimo em diferentes margens.

As alterações dos campos no Streamlit só atualizam o resultado após enviar o formulário. O resultado permanece identificado como última análise enviada.

## Dados e limitações

Os cálculos estão conectados ao backend, mas a fonte de anúncios permanece fictícia. Há apenas três exemplos para **JBL Tune 510BT / Áudio e fones / Novo**, ativados pela opção **Usar anúncios de exemplo**. Outro modelo, outra condição ou a opção desativada gera o cenário sem equivalentes. O 520BT nunca entra como equivalente ao 510BT neste exemplo.

Não há banco de dados, IA, embeddings, similaridade calculada nem métricas de avaliação nesta integração. `backend/demo_market.py` é o ponto a substituir pelo serviço de matching futuro. Não se infere crescimento de vendas nem demanda a partir dos gráficos.

## Publicar

O Streamlit precisa de um servidor Python (por exemplo, Streamlit Community Cloud). Ao implantar o repositório, configure a entrada **streamlit_app.py** e instale **requirements.txt**. A página única de formulário e resultados passa a ser a aplicação publicada.

O site estático hospedado no Sites não executa Streamlit. Atualizar o GitHub não publica automaticamente o servidor Python nem altera a prévia estática do Sites. O endereço `localhost:8501` funciona somente com o servidor local em execução.

O envio por URL é adequado a esta demonstração: os campos podem aparecer no histórico e nos logs de acesso. Para uma versão com dados privados, trocar o handoff por sessão/componente autenticado antes de uso real. Não coloque segredos em `config.js`.

## Testar

```bash
python -m unittest discover -s tests -v
node tests/frontend-handoff.cjs
```

Os testes verificam regra financeira, arredondamento, inviabilidade, ausência de equivalentes, validação dos parâmetros, envio do frontend e renderização das métricas/gráficos via Streamlit AppTest.

Referências oficiais: [formulários](https://docs.streamlit.io/develop/api-reference/execution-flow/st.form), [gráficos Plotly](https://docs.streamlit.io/develop/api-reference/charts/st.plotly_chart), [parâmetros de URL](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.query_params).
