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

O botão **Começar precificação** abre o formulário. **Usar exemplo** preenche os campos com valores de demonstração. **Como funciona** abre uma explicação do fluxo. O layout se adapta a desktop e celular.

## Escopo

Os anúncios, preços, margens e pontuações são exemplos fixos no HTML. O formulário demonstra a interação, sem calcular ou identificar produtos. Não há banco de dados, catálogo, histórico, exportação, armazenamento local, autenticação própria, integração com backend ou IA nesta etapa.

A imagem foi gerada com a ferramenta integrada Imagegen; o prompt está em `image-prompt.txt`. A pessoa retratada é sintética. O frontend usa identidade própria do Precifica.
