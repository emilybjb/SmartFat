import { state } from './state.js';

export const qs = (selector, root = document) => root.querySelector(selector);
export const qsa = (selector, root = document) => [...root.querySelectorAll(selector)];

export function money(value) {
  return Number(value || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

export function date(value) {
  if (!value) return '-';
  return new Date(value).toLocaleDateString('pt-BR', { timeZone: 'UTC' });
}

export function dateTime(value) {
  if (!value) return '-';
  return new Date(value).toLocaleString('pt-BR');
}

export function statusBadge(status) {
  const normalized = String(status || '').toLowerCase();
  const color = normalized === 'ativo' || normalized === 'pago' ? 'green' : normalized === 'pendente' ? 'orange' : 'red';
  return `<span class="badge badge-${color}">${status || '-'}</span>`;
}

export function toast(message, type = 'success') {
  const container = qs('#toast-container');
  const item = document.createElement('div');
  item.className = `toast ${type}`;
  item.textContent = message;
  container.appendChild(item);
  setTimeout(() => item.remove(), 3200);
}

export function setActiveView(view) {
  state.view = view;
  qsa('.nav-item').forEach((item) => item.classList.toggle('active', item.dataset.view === view));
  qs('#page-title').textContent = titleFor(view);
}

export function titleFor(view) {
  const titles = {
    dashboard: 'Dashboard',
    alunos: 'Alunos',
    acesso: 'Controle de acesso',
    treinos: 'Treinos e avaliacoes',
    planos: 'Planos',
    mensalidades: 'Mensalidades',
    financeiro: 'Financeiro'
  };
  return titles[view] || 'SmartFat';
}

export function openModal(title, body, onSubmit) {
  const root = qs('#modal-root');
  root.innerHTML = `
    <div class="modal-overlay">
      <form class="modal">
        <div class="modal-header">
          <h2 class="modal-title">${title}</h2>
          <button class="modal-close" type="button" aria-label="Fechar">×</button>
        </div>
        <div class="modal-body">
          ${body}
          <div class="modal-footer">
            <button class="btn btn-ghost" type="button" data-close>Cancelar</button>
            <button class="btn btn-primary" type="submit">Salvar</button>
          </div>
        </div>
      </form>
    </div>
  `;

  const form = qs('form', root);
  const close = () => root.innerHTML = '';
  qs('.modal-close', root).addEventListener('click', close);
  qs('[data-close]', root).addEventListener('click', close);
  qs('.modal-overlay', root).addEventListener('click', (event) => {
    if (event.target.classList.contains('modal-overlay')) close();
  });
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    await onSubmit(new FormData(form));
    close();
  });
}

export function options(items, idKey, textKey, selected) {
  return items.map((item) => {
    const id = item[idKey];
    const text = item[textKey];
    return `<option value="${id}" ${String(id) === String(selected || '') ? 'selected' : ''}>${text}</option>`;
  }).join('');
}

export function emptyState(text) {
  return `<div class="empty-state">${text}</div>`;
}
