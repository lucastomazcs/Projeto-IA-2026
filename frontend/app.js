// Somente interações de interface. Sem banco de dados ou análise de IA.
const form = document.querySelector('#product-form');
const status = document.querySelector('#preview-status');
document.querySelector('#fill-example').addEventListener('click', () => {
  const example = {product: 'JBL Tune 510BT', category: 'Áudio e fones', condition: 'Novo', cost: '120', shipping: '15', fees: '12', margin: '20'};
  for (const [id, value] of Object.entries(example)) document.getElementById(id).value = value;
  status.textContent = 'Formulário preenchido com um exemplo de demonstração.';
});
const help = document.querySelector('#help-dialog');
document.querySelector('#help-open').addEventListener('click', () => help.showModal());
document.querySelector('#help-close').addEventListener('click', () => help.close());
form.addEventListener('submit', event => {
  event.preventDefault();
  status.textContent = 'Visualização de exemplo. Os valores apresentados são fixos neste protótipo.';
  document.querySelector('.summary').scrollIntoView({behavior: 'smooth', block: 'center'});
});
document.querySelector('#reset').addEventListener('click', () => {
  form.reset();
  status.textContent = '';
  document.querySelector('#product').focus();
});
