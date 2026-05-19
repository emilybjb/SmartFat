import { api } from './api.js';
import { clearSession, setSession, state } from './state.js';
import { date, dateTime, emptyState, money, openModal, options, qs, qsa, setActiveView, statusBadge, toast } from './ui.js';

const view = qs('#view');

const views = {
  dashboard: renderDashboard,
  alunos: renderAlunos,
  cadastro: renderCadastro,
  acesso: renderAcesso,
  treinos: renderTreinos,
  planos: renderPlanos,
  mensalidades: renderMensalidades,
  financeiro: renderFinanceiro,
  relatorios: renderRelatorios
};

const roleViews = {
  admin: ['dashboard', 'alunos', 'cadastro', 'acesso', 'treinos', 'planos', 'mensalidades', 'financeiro', 'relatorios'],
  treinador: ['dashboard', 'alunos', 'treinos'],
  professor: ['dashboard', 'alunos', 'treinos'],
  aluno: ['dashboard', 'mensalidades', 'treinos', 'acesso'],
  recepcionista: ['acesso']
};

init();

function init() {
  qs('#login-form').addEventListener('submit', login);
  qs('#logout-button').addEventListener('click', logout);
  qs('#refresh-button').addEventListener('click', () => renderCurrent());
  qs('#sidebar-nav').addEventListener('click', navigate);
  document.addEventListener('input', sanitizeDocumentInput);
  window.addEventListener('session:expired', () => showLogin('Sessao expirada. Entre novamente.'));

  if (state.token) {
    showApp();
    renderCurrent();
  }
}

function sanitizeDocumentInput(event) {
  const input = event.target;
  if (!(input instanceof HTMLInputElement)) return;

  const limits = {
    CPF: 11,
    telefone: 11
  };
  const limit = limits[input.name];
  if (!limit) return;

  input.value = input.value.replace(/\D/g, '').slice(0, limit);
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
  if (!allowedViews().includes(item.dataset.view)) {
    toast('Seu perfil nao tem permissao para acessar esta area.', 'error');
    return;
  }
  setActiveView(item.dataset.view);
  renderCurrent();
}

function showApp() {
  qs('#login-page').classList.add('hidden');
  qs('#app').classList.remove('hidden');
  configureNavigation();
  const initials = (state.user?.nome || 'SF').split(' ').map((part) => part[0]).join('').slice(0, 2).toUpperCase();
  qs('#user-avatar').textContent = initials;
  qs('#user-name').textContent = state.user?.nome || 'SmartFat';
  qs('#user-role').textContent = state.user?.perfil || 'admin';
  const aviso = state.user?.aviso_acesso;
  if (aviso && aviso.permitido === false) {
    toast(`Acesso bloqueado: ${aviso.motivo}`, 'error');
  }
}

function showLogin(message = '') {
  qs('#app').classList.add('hidden');
  qs('#login-page').classList.remove('hidden');
  const error = qs('#login-error');
  error.textContent = message;
  error.style.display = message ? 'block' : 'none';
}

async function renderCurrent() {
  const allowed = allowedViews();
  if (!allowed.includes(state.view)) {
    setActiveView(allowed[0] || 'dashboard');
  }
  setActiveView(state.view);
  view.innerHTML = '<div class="loading">Carregando...</div>';
  try {
    await views[state.view]();
  } catch (error) {
    view.innerHTML = `<div class="empty-state">${error.message}</div>`;
    toast(error.message, 'error');
  }
}

function allowedViews() {
  const perfil = state.user?.perfil || 'admin';
  return roleViews[perfil] || roleViews.recepcionista;
}

function configureNavigation() {
  const allowed = allowedViews();
  qsa('.nav-item').forEach((item) => {
    item.classList.toggle('hidden', !allowed.includes(item.dataset.view));
  });
  if (!allowed.includes(state.view)) {
    state.view = allowed[0] || 'dashboard';
  }
}

async function loadBase() {
  const [alunos, planos] = await Promise.all([api.alunos(), api.planos()]);
  state.cache.alunos = alunos;
  state.cache.planos = planos;
}

async function renderDashboard() {
  if (state.user?.perfil === 'aluno') return renderAlunoDashboard();
  if (['treinador', 'professor'].includes(state.user?.perfil)) return renderTreinadorDashboard();

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

async function renderAlunoDashboard() {
  const [mensalidades, treinos, acessos, status] = await Promise.all([
    api.mensalidades(),
    api.treinos(),
    api.acessos(),
    api.acessoStatus()
  ]);
  const pendentes = mensalidades.filter((item) => item.status === 'Pendente');

  view.innerHTML = `
    ${accessNotice(status)}
    <div class="stats-grid">
      ${stat('Faturas pendentes', pendentes.length, pendentes.length ? 'orange' : 'green')}
      ${stat('Treinos designados', treinos.length, 'blue')}
      ${stat('Acessos registrados', acessos.length, 'green')}
    </div>
    <div class="grid-2">
      ${tableCard('Minhas faturas', ['Vencimento', 'Valor', 'Status'], mensalidades.slice(0, 6).map((item) => [
        date(item.dataVencimento),
        money(item.valor),
        statusBadge(item.status)
      ]))}
      ${tableCard('Meus treinos', ['Data', 'Descricao'], treinos.slice(0, 6).map((item) => [
        date(item.data),
        item.descricao
      ]))}
    </div>
  `;
}

async function renderTreinadorDashboard() {
  const [alunos, treinos] = await Promise.all([api.alunos(), api.treinos()]);
  view.innerHTML = `
    <div class="stats-grid">
      ${stat('Alunos acompanhados', alunos.length, 'blue')}
      ${stat('Treinos designados', treinos.length, 'green')}
    </div>
    <div class="grid-2">
      ${tableCard('Alunos', ['Nome', 'Plano', 'Status'], alunos.slice(0, 8).map((aluno) => [
        aluno.nome,
        aluno.plano_nome || '-',
        statusBadge(aluno.status)
      ]))}
      ${tableCard('Ultimos treinos', ['Aluno', 'Data', 'Descricao'], treinos.slice(0, 8).map((item) => [
        item.aluno_nome,
        date(item.data),
        item.descricao
      ]))}
    </div>
  `;
}

async function renderAlunos() {
  await loadBase();
  const canManage = state.user?.perfil === 'admin';
  const rows = state.cache.alunos.map((aluno) => [
    aluno.nome,
    aluno.CPF,
    aluno.telefone || '-',
    aluno.plano_nome || '-',
    statusBadge(aluno.status),
    canManage ? actions([
      ['Editar', `edit:${aluno.idAluno}`],
      ['Remover', `remove:${aluno.idAluno}`, 'danger']
    ]) : '-'
  ]);

  view.innerHTML = canManage
    ? cardWithAction('Alunos cadastrados', 'Novo aluno', table(['Nome', 'CPF', 'Telefone', 'Plano', 'Status', 'Acoes'], rows))
    : tableCard('Alunos cadastrados', ['Nome', 'CPF', 'Telefone', 'Plano', 'Status', 'Acoes'], rows);
  if (canManage) qs('[data-action="new"]').addEventListener('click', () => alunoModal());
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

async function renderCadastro() {
  state.cache.planos = await api.planos();
  const vencimentoPadrao = dateInputValue(30);

  view.innerHTML = `
    <div class="grid-2">
      <div class="card">
        <div class="card-header"><h2 class="card-title">Cadastrar aluno</h2></div>
        <form id="student-register-form" class="form-stack">
          <div class="form-grid">
            ${input('nome', 'Nome completo', '', true)}
            ${input('CPF', 'CPF', '', true)}
            ${input('telefone', 'Telefone')}
            ${input('email', 'E-mail de login', '', true, 'email')}
            ${input('senha', 'Senha inicial', '', true, 'password')}
            <label class="form-group">
              <span class="form-label">Plano</span>
              <select class="form-select" name="Plano_idPlano" required>${options(state.cache.planos, 'idPlano', 'nome')}</select>
            </label>
            ${select('status', 'Status', [['Ativo', 'Ativo'], ['Inativo', 'Inativo']], 'Ativo')}
            ${input('mensalidade_valor', 'Valor da mensalidade', '', false, 'number', '0.01')}
            ${input('dataVencimento', 'Vencimento inicial', vencimentoPadrao, true, 'date')}
          </div>
          <div class="form-actions">
            <button class="btn btn-primary" type="submit">Cadastrar aluno</button>
          </div>
        </form>
      </div>

      <div class="card">
        <div class="card-header"><h2 class="card-title">Cadastrar professor</h2></div>
        <form id="teacher-register-form" class="form-stack">
          <div class="form-grid">
            ${input('nome', 'Nome completo', '', true)}
            ${input('email', 'E-mail de login', '', true, 'email')}
            ${input('senha', 'Senha inicial', '', true, 'password')}
            ${select('perfil', 'Perfil', [['treinador', 'Treinador'], ['professor', 'Professor']], 'treinador')}
          </div>
          <div class="form-actions">
            <button class="btn btn-primary" type="submit">Cadastrar professor</button>
          </div>
        </form>
      </div>
    </div>
  `;

  qs('#student-register-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    try {
      const payload = Object.fromEntries(new FormData(event.currentTarget).entries());
      await api.cadastrarUsuario({ ...payload, tipo: 'aluno' });
      toast('Aluno cadastrado com login e mensalidade inicial');
      renderCurrent();
    } catch (error) {
      toast(error.message, 'error');
    }
  });

  qs('#teacher-register-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    try {
      const payload = Object.fromEntries(new FormData(event.currentTarget).entries());
      await api.cadastrarUsuario({ ...payload, tipo: 'professor' });
      toast('Professor cadastrado com sucesso');
      event.currentTarget.reset();
    } catch (error) {
      toast(error.message, 'error');
    }
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
  const isAdmin = state.user?.perfil === 'admin';
  if (isAdmin) await loadBase();
  const mensalidades = await api.mensalidades();
  const rows = mensalidades.map((mensalidade) => {
    const payAction = mensalidade.status === 'Pago' ? '-' : actions([['Pagar', `pay:${mensalidade.idMensalidade}`]]);
    return isAdmin
      ? [mensalidade.aluno_nome, date(mensalidade.dataVencimento), money(mensalidade.valor), statusBadge(mensalidade.status), payAction]
      : [date(mensalidade.dataVencimento), money(mensalidade.valor), statusBadge(mensalidade.status), payAction];
  });
  const headers = isAdmin ? ['Aluno', 'Vencimento', 'Valor', 'Status', 'Acoes'] : ['Vencimento', 'Valor', 'Status', 'Acoes'];

  view.innerHTML = isAdmin
    ? cardWithAction('Mensalidades', 'Nova mensalidade', table(headers, rows))
    : tableCard('Minhas mensalidades', headers, rows);
  if (isAdmin) qs('[data-action="new"]').addEventListener('click', mensalidadeModal);
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
  if (state.user?.perfil === 'aluno') return renderMeuAcesso();

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
    ${tableCard('Historico de acesso', ['Aluno', 'Entrada', 'Resultado', 'Motivo'], acessos.map((item) => [
      item.aluno_nome,
      dateTime(item.dataHoraEntrada),
      statusBadge(Number(item.permitido) === 0 ? 'Negado' : 'Liberado'),
      item.motivoNegacao || '-'
    ]))}
  `;
  qs('#access-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    try {
      const result = await api.registrarEntrada(new FormData(event.currentTarget).get('aluno_id'));
      toast(result.motivo || 'Entrada liberada');
    } catch (error) {
      toast(`Entrada negada: ${error.message}`, 'error');
    }
    renderCurrent();
  });
}

async function renderMeuAcesso() {
  const [status, acessos] = await Promise.all([api.acessoStatus(), api.acessos()]);
  view.innerHTML = `
    ${accessNotice(status)}
    ${tableCard('Meu historico de acesso', ['Entrada', 'Resultado', 'Motivo'], acessos.map((item) => [
      dateTime(item.dataHoraEntrada),
      statusBadge(Number(item.permitido) === 0 ? 'Negado' : 'Liberado'),
      item.motivoNegacao || '-'
    ]))}
  `;
}

async function renderTreinos() {
  const isAluno = state.user?.perfil === 'aluno';
  if (!isAluno) await loadBase();
  const [treinos, avaliacoes] = await Promise.all([api.treinos(), api.avaliacoes()]);
  const treinoHeaders = isAluno ? ['Data', 'Descricao'] : ['Aluno', 'Data', 'Descricao', 'Acoes'];
  const avaliacaoHeaders = isAluno ? ['Peso', 'Altura'] : ['Aluno', 'Peso', 'Altura', 'Acoes'];
  view.innerHTML = `
    ${isAluno ? '' : `
      <div class="split-actions">
        <button class="btn btn-primary" data-action="new-training" type="button">Novo treino</button>
        <button class="btn btn-ghost" data-action="new-evaluation" type="button">Nova avaliacao</button>
      </div>
    `}
    <div class="grid-2">
      ${tableCard(isAluno ? 'Meus treinos' : 'Treinos', treinoHeaders, treinos.map((item) => (
        isAluno
          ? [date(item.data), item.descricao]
          : [item.aluno_nome, date(item.data), item.descricao, actions([
              ['Editar', `edit-training:${item.idTreino}`],
              ['Remover', `remove-training:${item.idTreino}`, 'danger']
            ])]
      )))}
      ${tableCard(isAluno ? 'Minhas avaliacoes fisicas' : 'Avaliacoes fisicas', avaliacaoHeaders, avaliacoes.map((item) => (
        isAluno
          ? [`${item.peso || '-'} kg`, `${item.altura || '-'} m`]
          : [item.aluno_nome, `${item.peso || '-'} kg`, `${item.altura || '-'} m`, actions([
              ['Editar', `edit-evaluation:${item.idAvaliacaoFisica}`],
              ['Remover', `remove-evaluation:${item.idAvaliacaoFisica}`, 'danger']
            ])]
      )))}
    </div>
  `;
  if (!isAluno) {
    qs('[data-action="new-training"]').addEventListener('click', treinoModal);
    qs('[data-action="new-evaluation"]').addEventListener('click', avaliacaoModal);
    bindActions({
      'edit-training': (id) => treinoModal(treinos.find((item) => String(item.idTreino) === id)),
      'remove-training': async (id) => {
        await api.removerTreino(id);
        toast('Treino removido');
        renderCurrent();
      },
      'edit-evaluation': (id) => avaliacaoModal(avaliacoes.find((item) => String(item.idAvaliacaoFisica) === id)),
      'remove-evaluation': async (id) => {
        await api.removerAvaliacao(id);
        toast('Avaliacao removida');
        renderCurrent();
      }
    });
  }
}

function treinoModal(treino = {}) {
  openModal('Treino', `
    <div class="form-grid">
      <label class="form-group">
        <span class="form-label">Aluno</span>
        <select class="form-select" name="Aluno_idTreino" required>${options(state.cache.alunos, 'idAluno', 'nome', treino.Aluno_idTreino)}</select>
      </label>
      ${input('data', 'Data', dateInputFromApi(treino.data), true, 'date')}
      ${input('descricao', 'Descricao', treino.descricao, true)}
    </div>
  `, async (form) => {
    const payload = Object.fromEntries(form.entries());
    if (treino.idTreino) {
      await api.atualizarTreino(treino.idTreino, payload);
    } else {
      await api.criarTreino(payload);
    }
    toast('Treino salvo');
    renderCurrent();
  });
}

function avaliacaoModal(avaliacao = {}) {
  openModal('Avaliacao fisica', `
    <div class="form-grid">
      <label class="form-group">
        <span class="form-label">Aluno</span>
        <select class="form-select" name="Aluno_idAluno" required>${options(state.cache.alunos, 'idAluno', 'nome', avaliacao.Aluno_idAluno)}</select>
      </label>
      ${input('peso', 'Peso', avaliacao.peso, true, 'number', '0.01')}
      ${input('altura', 'Altura', avaliacao.altura, true, 'number', '0.01')}
    </div>
  `, async (form) => {
    const payload = Object.fromEntries(form.entries());
    if (avaliacao.idAvaliacaoFisica) {
      await api.atualizarAvaliacao(avaliacao.idAvaliacaoFisica, payload);
    } else {
      await api.criarAvaliacao(payload);
    }
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

async function renderRelatorios() {
  const [financeiro, acesso] = await Promise.all([api.relatorioFinanceiro(), api.relatorioAcesso()]);

  view.innerHTML = `
    <div class="grid-2">
      ${tableCard('Relatorio financeiro', ['Periodo', 'Recebido', 'Pendente', 'Mensalidades'], financeiro.map((item) => [
        item.periodo,
        money(item.recebido),
        money(item.pendente),
        item.total_mensalidades
      ]))}
      ${tableCard('Relatorio de acesso', ['Aluno', 'Tentativas', 'Liberados', 'Negados', 'Ultimo motivo'], acesso.map((item) => [
        item.aluno_nome,
        item.total_tentativas,
        item.liberados || 0,
        item.negados || 0,
        item.ultimo_motivo_negado || '-'
      ]))}
    </div>
  `;
}

function accessNotice(status) {
  const type = status?.permitido ? 'success' : 'error';
  const title = status?.permitido ? 'Acesso liberado' : 'Acesso bloqueado';
  return `
    <div class="notice notice-${type} mb-4">
      <strong>${title}</strong>
      <span>${status?.motivo || 'Nao foi possivel validar sua situacao de acesso.'}</span>
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
  const numericAttrs = {
    CPF: 'maxlength="11" minlength="11" inputmode="numeric" pattern="\\d{11}"',
    telefone: 'maxlength="11" inputmode="numeric" pattern="\\d{0,11}"'
  };
  const extraAttrs = numericAttrs[name] || '';
  return `
    <label class="form-group">
      <span class="form-label">${label}</span>
      <input class="form-input" name="${name}" type="${type}" value="${value || ''}" ${required ? 'required' : ''} ${step ? `step="${step}"` : ''} ${extraAttrs}>
    </label>
  `;
}

function dateInputValue(daysFromToday = 0) {
  const date = new Date();
  date.setDate(date.getDate() + daysFromToday);
  return date.toISOString().slice(0, 10);
}

function dateInputFromApi(value) {
  if (!value) return '';
  return new Date(value).toISOString().slice(0, 10);
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
