import { api } from './api.js';
import { clearSession, setSession, state } from './state.js';
import { date, dateTime, emptyState, money, openModal, options, qs, qsa, setActiveView, statusBadge, toast } from './ui.js';

const view = qs('#view');

const views = {
  dashboard: renderDashboard,
  alunos: renderAlunos,
  acesso: renderAcesso,
  treinos: renderTreinos,
  planos: renderPlanos,
  mensalidades: renderMensalidades,
  financeiro: renderFinanceiro
};

init();

function init() {
  qs('#login-form').addEventListener('submit', login);
  qs('#logout-button').addEventListener('click', logout);
  qs('#refresh-button').addEventListener('click', () => renderCurrent());
  qs('#sidebar-nav').addEventListener('click', navigate);
  window.addEventListener('session:expired', () => showLogin('Sessao expirada. Entre novamente.'));

  if (state.token) {
    showApp();
    renderCurrent();
  }
}

async function login(event) {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  try {
    const session = await api.login({
      email: form.get('email'),
      senha: form.get('senha')
    });
    setSession(session);
    qs('#login-error').style.display = 'none';
    showApp();
    await renderCurrent();
  } catch (error) {
    showLogin(error.message);
  }
}

function logout() {
  clearSession();
  showLogin();
}

function navigate(event) {
  const item = event.target.closest('.nav-item');
  if (!item) return;
  setActiveView(item.dataset.view);
  renderCurrent();
}

function showApp() {
  qs('#login-page').classList.add('hidden');
  qs('#app').classList.remove('hidden');
  const initials = (state.user?.nome || 'SF').split(' ').map((part) => part[0]).join('').slice(0, 2).toUpperCase();
  qs('#user-avatar').textContent = initials;
  qs('#user-name').textContent = state.user?.nome || 'SmartFat';
  qs('#user-role').textContent = state.user?.perfil || 'admin';
}

function showLogin(message = '') {
  qs('#app').classList.add('hidden');
  qs('#login-page').classList.remove('hidden');
  const error = qs('#login-error');
  error.textContent = message;
  error.style.display = message ? 'block' : 'none';
}

async function renderCurrent() {
  setActiveView(state.view);
  view.innerHTML = '<div class="loading">Carregando...</div>';
  try {
    await views[state.view]();
  } catch (error) {
    view.innerHTML = `<div class="empty-state">${error.message}</div>`;
    toast(error.message, 'error');
  }
}

async function loadBase() {
  const [alunos, planos] = await Promise.all([api.alunos(), api.planos()]);
  state.cache.alunos = alunos;
  state.cache.planos = planos;
}

async function renderDashboard() {
  const [dashboard, financeiro, mensalidades, acessos] = await Promise.all([
    api.dashboard(),
    api.financeiro(),
    api.mensalidades(),
    api.acessos()
  ]);

  view.innerHTML = `
    <div class="stats-grid">
      ${stat('Alunos ativos', dashboard.alunos_ativos, 'orange')}
      ${stat('Receita do mes', money(dashboard.receita_mes), 'green')}
      ${stat('Pendencias', dashboard.mensalidades_pendentes, 'red')}
      ${stat('Acessos hoje', dashboard.acessos_hoje, 'blue')}
    </div>
    <div class="grid-2">
      ${tableCard('Mensalidades recentes', ['Aluno', 'Vencimento', 'Valor', 'Status'], mensalidades.slice(0, 6).map((item) => [
        item.aluno_nome,
        date(item.dataVencimento),
        money(item.valor),
        statusBadge(item.status)
      ]))}
      ${tableCard('Ultimos acessos', ['Aluno', 'Entrada'], acessos.slice(0, 6).map((item) => [
        item.aluno_nome,
        dateTime(item.dataHoraEntrada)
      ]))}
    </div>
    <div class="card mt-4">
      <div class="card-header"><h2 class="card-title">Resumo financeiro</h2></div>
      <div class="inline-metrics">
        <span>Recebido: <strong>${money(financeiro.total_recebido)}</strong></span>
        <span>Pendente: <strong>${money(financeiro.total_pendente)}</strong></span>
        <span>Alunos ativos: <strong>${financeiro.total_alunos_ativos}</strong></span>
      </div>
    </div>
  `;
}

async function renderAlunos() {
  await loadBase();
  const rows = state.cache.alunos.map((aluno) => [
    aluno.nome,
    aluno.CPF,
    aluno.telefone || '-',
    aluno.plano_nome || '-',
    statusBadge(aluno.status),
    actions([
      ['Editar', `edit:${aluno.idAluno}`],
      ['Remover', `remove:${aluno.idAluno}`, 'danger']
    ])
  ]);

  view.innerHTML = cardWithAction('Alunos cadastrados', 'Novo aluno', table(['Nome', 'CPF', 'Telefone', 'Plano', 'Status', 'Acoes'], rows));
  qs('[data-action="new"]').addEventListener('click', () => alunoModal());
  bindActions({
    edit: (id) => alunoModal(state.cache.alunos.find((item) => String(item.idAluno) === id)),
    remove: async (id) => {
      await api.removerAluno(id);
      toast('Aluno removido');
      renderCurrent();
    }
  });
}

function alunoModal(aluno = {}) {
  openModal('Aluno', `
    <div class="form-grid">
      ${input('nome', 'Nome', aluno.nome, true)}
      ${input('CPF', 'CPF', aluno.CPF, !aluno.idAluno)}
      ${input('telefone', 'Telefone', aluno.telefone)}
      ${select('status', 'Status', [['Ativo', 'Ativo'], ['Inativo', 'Inativo']], aluno.status || 'Ativo')}
      <label class="form-group">
        <span class="form-label">Plano</span>
        <select class="form-select" name="Plano_idPlano">${options(state.cache.planos, 'idPlano', 'nome', aluno.Plano_idPlano)}</select>
      </label>
    </div>
  `, async (form) => {
    const payload = Object.fromEntries(form.entries());
    if (aluno.idAluno) {
      await api.atualizarAluno(aluno.idAluno, payload);
    } else {
      await api.criarAluno(payload);
    }
    toast('Aluno salvo');
    renderCurrent();
  });
}

async function renderPlanos() {
  state.cache.planos = await api.planos();
  const rows = state.cache.planos.map((plano) => [
    plano.nome,
    money(plano.valor),
    `${plano.duracao || 30} dias`,
    actions([
      ['Editar', `edit:${plano.idPlano}`],
      ['Remover', `remove:${plano.idPlano}`, 'danger']
    ])
  ]);

  view.innerHTML = cardWithAction('Planos', 'Novo plano', table(['Nome', 'Valor', 'Duracao', 'Acoes'], rows));
  qs('[data-action="new"]').addEventListener('click', () => planoModal());
  bindActions({
    edit: (id) => planoModal(state.cache.planos.find((item) => String(item.idPlano) === id)),
    remove: async (id) => {
      await api.removerPlano(id);
      toast('Plano removido');
      renderCurrent();
    }
  });
}

function planoModal(plano = {}) {
  openModal('Plano', `
    <div class="form-grid">
      ${input('nome', 'Nome', plano.nome, true)}
      ${input('valor', 'Valor', plano.valor, true, 'number', '0.01')}
      ${input('duracao', 'Duracao em dias', plano.duracao || 30, true, 'number')}
    </div>
  `, async (form) => {
    const payload = Object.fromEntries(form.entries());
    if (plano.idPlano) {
      await api.atualizarPlano(plano.idPlano, payload);
    } else {
      await api.criarPlano(payload);
    }
    toast('Plano salvo');
    renderCurrent();
  });
}

async function renderMensalidades() {
  await loadBase();
  const mensalidades = await api.mensalidades();
  const rows = mensalidades.map((mensalidade) => [
    mensalidade.aluno_nome,
    date(mensalidade.dataVencimento),
    money(mensalidade.valor),
    statusBadge(mensalidade.status),
    mensalidade.status === 'Pago' ? '-' : actions([['Pagar', `pay:${mensalidade.idMensalidade}`]])
  ]);

  view.innerHTML = cardWithAction('Mensalidades', 'Nova mensalidade', table(['Aluno', 'Vencimento', 'Valor', 'Status', 'Acoes'], rows));
  qs('[data-action="new"]').addEventListener('click', mensalidadeModal);
  bindActions({
    pay: async (id) => {
      await api.pagarMensalidade(id);
      toast('Mensalidade marcada como paga');
      renderCurrent();
    }
  });
}

function mensalidadeModal() {
  openModal('Mensalidade', `
    <div class="form-grid">
      <label class="form-group">
        <span class="form-label">Aluno</span>
        <select class="form-select" name="Aluno_idAluno" required>${options(state.cache.alunos, 'idAluno', 'nome')}</select>
      </label>
      ${input('valor', 'Valor', '', true, 'number', '0.01')}
      ${input('dataVencimento', 'Vencimento', '', true, 'date')}
    </div>
  `, async (form) => {
    await api.criarMensalidade(Object.fromEntries(form.entries()));
    toast('Mensalidade criada');
    renderCurrent();
  });
}

async function renderAcesso() {
  await loadBase();
  const acessos = await api.acessos();
  view.innerHTML = `
    <div class="card mb-4">
      <div class="card-header"><h2 class="card-title">Registrar entrada</h2></div>
      <form class="form-inline" id="access-form">
        <select class="form-select" name="aluno_id" required>${options(state.cache.alunos, 'idAluno', 'nome')}</select>
        <button class="btn btn-primary" type="submit">Liberar entrada</button>
      </form>
    </div>
    ${tableCard('Historico de acesso', ['Aluno', 'Entrada', 'Saida'], acessos.map((item) => [
      item.aluno_nome,
      dateTime(item.dataHoraEntrada),
      dateTime(item.dataHoraSaida)
    ]))}
  `;
  qs('#access-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    await api.registrarEntrada(new FormData(event.currentTarget).get('aluno_id'));
    toast('Entrada liberada');
    renderCurrent();
  });
}

async function renderTreinos() {
  await loadBase();
  const [treinos, avaliacoes] = await Promise.all([api.treinos(), api.avaliacoes()]);
  view.innerHTML = `
    <div class="split-actions">
      <button class="btn btn-primary" data-action="new-training" type="button">Novo treino</button>
      <button class="btn btn-ghost" data-action="new-evaluation" type="button">Nova avaliacao</button>
    </div>
    <div class="grid-2">
      ${tableCard('Treinos', ['Aluno', 'Data', 'Descricao'], treinos.map((item) => [
        item.aluno_nome,
        date(item.data),
        item.descricao
      ]))}
      ${tableCard('Avaliacoes fisicas', ['Aluno', 'Peso', 'Altura'], avaliacoes.map((item) => [
        item.aluno_nome,
        `${item.peso || '-'} kg`,
        `${item.altura || '-'} m`
      ]))}
    </div>
  `;
  qs('[data-action="new-training"]').addEventListener('click', treinoModal);
  qs('[data-action="new-evaluation"]').addEventListener('click', avaliacaoModal);
}

function treinoModal() {
  openModal('Treino', `
    <div class="form-grid">
      <label class="form-group">
        <span class="form-label">Aluno</span>
        <select class="form-select" name="Aluno_idTreino" required>${options(state.cache.alunos, 'idAluno', 'nome')}</select>
      </label>
      ${input('data', 'Data', '', true, 'date')}
      ${input('descricao', 'Descricao', '', true)}
    </div>
  `, async (form) => {
    await api.criarTreino(Object.fromEntries(form.entries()));
    toast('Treino salvo');
    renderCurrent();
  });
}

function avaliacaoModal() {
  openModal('Avaliacao fisica', `
    <div class="form-grid">
      <label class="form-group">
        <span class="form-label">Aluno</span>
        <select class="form-select" name="Aluno_idAluno" required>${options(state.cache.alunos, 'idAluno', 'nome')}</select>
      </label>
      ${input('peso', 'Peso', '', true, 'number', '0.01')}
      ${input('altura', 'Altura', '', true, 'number', '0.01')}
    </div>
  `, async (form) => {
    await api.criarAvaliacao(Object.fromEntries(form.entries()));
    toast('Avaliacao salva');
    renderCurrent();
  });
}

async function renderFinanceiro() {
  const [financeiro, mensalidades] = await Promise.all([api.financeiro(), api.mensalidades()]);
  const pagas = mensalidades.filter((item) => item.status === 'Pago');
  const pendentes = mensalidades.filter((item) => item.status === 'Pendente');

  view.innerHTML = `
    <div class="stats-grid">
      ${stat('Total recebido', money(financeiro.total_recebido), 'green')}
      ${stat('Total pendente', money(financeiro.total_pendente), 'orange')}
      ${stat('Alunos ativos', financeiro.total_alunos_ativos, 'blue')}
    </div>
    <div class="grid-2">
      ${tableCard('Recebimentos', ['Aluno', 'Vencimento', 'Valor'], pagas.map((item) => [
        item.aluno_nome,
        date(item.dataVencimento),
        money(item.valor)
      ]))}
      ${tableCard('Pendencias', ['Aluno', 'Vencimento', 'Valor'], pendentes.map((item) => [
        item.aluno_nome,
        date(item.dataVencimento),
        money(item.valor)
      ]))}
    </div>
  `;
}

function stat(label, value, color) {
  return `
    <article class="stat-card ${color}">
      <div class="stat-label">${label}</div>
      <div class="stat-value">${value}</div>
      <div class="stat-icon">■</div>
    </article>
  `;
}

function cardWithAction(title, buttonText, content) {
  return `
    <div class="card">
      <div class="card-header">
        <h2 class="card-title">${title}</h2>
        <button class="btn btn-primary" data-action="new" type="button">${buttonText}</button>
      </div>
      ${content}
    </div>
  `;
}

function tableCard(title, headers, rows) {
  return `
    <div class="card">
      <div class="card-header"><h2 class="card-title">${title}</h2></div>
      ${table(headers, rows)}
    </div>
  `;
}

function table(headers, rows) {
  if (!rows.length) return emptyState('Nenhum registro encontrado');
  return `
    <div class="table-wrap">
      <table>
        <thead><tr>${headers.map((header) => `<th>${header}</th>`).join('')}</tr></thead>
        <tbody>
          ${rows.map((row) => `<tr>${row.map((cell) => `<td>${cell ?? '-'}</td>`).join('')}</tr>`).join('')}
        </tbody>
      </table>
    </div>
  `;
}

function actions(items) {
  return `
    <div class="flex gap-2">
      ${items.map(([label, action, type]) => `<button class="btn btn-sm ${type === 'danger' ? 'btn-danger' : 'btn-ghost'}" data-action="${action}" type="button">${label}</button>`).join('')}
    </div>
  `;
}

function bindActions(handlers) {
  qsa('[data-action*=":"]').forEach((button) => {
    button.addEventListener('click', () => {
      const [name, id] = button.dataset.action.split(':');
      handlers[name]?.(id);
    });
  });
}

function input(name, label, value = '', required = false, type = 'text', step = '') {
  return `
    <label class="form-group">
      <span class="form-label">${label}</span>
      <input class="form-input" name="${name}" type="${type}" value="${value || ''}" ${required ? 'required' : ''} ${step ? `step="${step}"` : ''}>
    </label>
  `;
}

function select(name, label, items, selected) {
  return `
    <label class="form-group">
      <span class="form-label">${label}</span>
      <select class="form-select" name="${name}">
        ${items.map(([value, text]) => `<option value="${value}" ${value === selected ? 'selected' : ''}>${text}</option>`).join('')}
      </select>
    </label>
  `;
}
