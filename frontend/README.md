# Precifica — protótipo de frontend

Interface em português feita com HTML, CSS e JavaScript, sem dependências de instalação.

## Executar

Abra `index.html` no navegador ou execute, a partir da raiz do repositório:

```bash
node frontend/serve.cjs
```

Acesse `http://127.0.0.1:4173`. Para encerrar o servidor, pressione Ctrl+C.

## Páginas

- `index.html` e `landing.css`: apresentação comercial, benefícios, funcionamento e dúvidas frequentes.
- `app.html`, `style.css` e `app.js`: formulário de produto e custos, resultado ilustrativo e comparação de anúncios.
- `assets/empreendedora.png`: imagem sintética gerada com Imagegen para o projeto.

O botão **Começar precificação** abre o formulário. **Usar exemplo** preenche os campos de demonstração. **Calcular no Streamlit** envia os dados à aplicação Python configurada em `config.js` (localmente, `http://localhost:8501/`). **Como funciona** abre uma explicação do fluxo. O layout se adapta a desktop e celular.

## Escopo

Os cartões e anúncios no HTML continuam como uma prévia estática. Os cálculos e o matching Sentence Transformers/cosseno são executados no Streamlit, com os dados CSV locais em `data/sample/`. O catálogo ainda é sintético e não usa banco de dados de produção. Para executar os serviços e configurar um endereço publicado, consulte [docs/streamlit.md](../docs/streamlit.md).

A imagem foi gerada com a ferramenta integrada Imagegen; o prompt está em `image-prompt.txt`. A pessoa retratada é sintética. O frontend usa identidade própria do Precifica.
