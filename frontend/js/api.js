import { clearSession, state } from './state.js';

const API_BASE = '/api';

async function request(path, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {})
  };

  if (state.token) {
    headers.Authorization = `Bearer ${state.token}`;
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers
  });

  if (response.status === 401) {
    clearSession();
    window.dispatchEvent(new CustomEvent('session:expired'));
  }

  const text = await response.text();
  const data = text ? JSON.parse(text) : null;

  if (!response.ok) {
    throw new Error(data?.erro || data?.motivo || data?.msg || 'Erro na requisicao');
  }

  return data;
}

export const api = {
  login: (payload) => request('/auth/login', { method: 'POST', body: JSON.stringify(payload) }),
  cadastrarUsuario: (payload) => request('/auth/cadastro', { method: 'POST', body: JSON.stringify(payload) }),
  dashboard: () => request('/relatorios/dashboard'),
  financeiro: () => request('/financeiro/resumo'),
  alunos: () => request('/alunos/'),
  criarAluno: (payload) => request('/alunos/', { method: 'POST', body: JSON.stringify(payload) }),
  atualizarAluno: (id, payload) => request(`/alunos/${id}`, { method: 'PUT', body: JSON.stringify(payload) }),
  removerAluno: (id) => request(`/alunos/${id}`, { method: 'DELETE' }),
  planos: () => request('/planos/'),
  criarPlano: (payload) => request('/planos/', { method: 'POST', body: JSON.stringify(payload) }),
  atualizarPlano: (id, payload) => request(`/planos/${id}`, { method: 'PUT', body: JSON.stringify(payload) }),
  removerPlano: (id) => request(`/planos/${id}`, { method: 'DELETE' }),
  mensalidades: () => request('/mensalidades/'),
  criarMensalidade: (payload) => request('/mensalidades/', { method: 'POST', body: JSON.stringify(payload) }),
  pagarMensalidade: (id) => request(`/mensalidades/${id}/pagar`, { method: 'PUT' }),
  acessos: () => request('/acesso/'),
  acessoStatus: () => request('/acesso/status'),
  registrarEntrada: (aluno_id) => request('/acesso/entrada', { method: 'POST', body: JSON.stringify({ aluno_id }) }),
  treinos: () => request('/treinos/'),
  criarTreino: (payload) => request('/treinos/', { method: 'POST', body: JSON.stringify(payload) }),
  atualizarTreino: (id, payload) => request(`/treinos/${id}`, { method: 'PUT', body: JSON.stringify(payload) }),
  removerTreino: (id) => request(`/treinos/${id}`, { method: 'DELETE' }),
  avaliacoes: () => request('/treinos/avaliacoes'),
  criarAvaliacao: (payload) => request('/treinos/avaliacoes', { method: 'POST', body: JSON.stringify(payload) }),
  atualizarAvaliacao: (id, payload) => request(`/treinos/avaliacoes/${id}`, { method: 'PUT', body: JSON.stringify(payload) }),
  removerAvaliacao: (id) => request(`/treinos/avaliacoes/${id}`, { method: 'DELETE' }),
  relatorioFinanceiro: () => request('/relatorios/financeiro'),
  relatorioAcesso: () => request('/relatorios/acesso')
};
