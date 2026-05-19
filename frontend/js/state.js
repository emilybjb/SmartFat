const TOKEN_KEY = 'smartfat_token';
const USER_KEY = 'smartfat_user';

export const state = {
  view: 'dashboard',
  token: localStorage.getItem(TOKEN_KEY),
  user: JSON.parse(localStorage.getItem(USER_KEY) || 'null'),
  cache: {
    alunos: [],
    planos: []
  }
};

export function setSession(session) {
  state.token = session.token;
  state.user = {
    nome: session.nome,
    perfil: session.perfil,
    aluno_id: session.aluno_id,
    aviso_acesso: session.aviso_acesso
  };
  localStorage.setItem(TOKEN_KEY, session.token);
  localStorage.setItem(USER_KEY, JSON.stringify(state.user));
}

export function clearSession() {
  state.token = null;
  state.user = null;
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}
