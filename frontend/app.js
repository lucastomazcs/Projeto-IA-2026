// O formulário envia os dados para a aplicação Python/Streamlit configurada.
const form = document.querySelector('#product-form');
const status = document.querySelector('#preview-status');
document.querySelector('#fill-example').addEventListener('click', () => {
  const example = {product: 'JBL Tune 510BT', category: 'Fones de ouvido', condition: 'Novo', cost: '120', shipping: '15', fees: '12', margin: '20'};
  for (const [id, value] of Object.entries(example)) document.getElementById(id).value = value;
  status.textContent = 'Formulário preenchido com um exemplo de demonstração.';
});
const help = document.querySelector('#help-dialog');
document.querySelector('#help-open').addEventListener('click', () => help.showModal());
document.querySelector('#help-close').addEventListener('click', () => help.close());
form.addEventListener('submit', event => {
  event.preventDefault();
  const values = Object.fromEntries(['product', 'category', 'condition', 'cost', 'shipping', 'fees', 'margin'].map(id => [id, document.getElementById(id).value]));
  if (Number(values.fees) + Number(values.margin) >= 100) {
    status.textContent = 'Taxas e margem precisam somar menos que 100%.';
    return;
  }
  try {
    const target = new URL(window.PRECIFICA_CONFIG.streamlitUrl);
    if (!['http:', 'https:'].includes(target.protocol)) throw new Error('URL inválida');
    for (const [key, value] of Object.entries(values)) target.searchParams.set(key, value);
    target.searchParams.set('analisar', '1');
    window.location.assign(target.href);
  } catch {
    status.textContent = 'Configure a URL da aplicação Streamlit em frontend/config.js.';
  }
});
document.querySelector('#reset').addEventListener('click', () => {
  form.reset();
  status.textContent = '';
  document.querySelector('#product').focus();
});
