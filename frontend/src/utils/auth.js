const TOKEN_KEY = 'lung_diagnosis_token';
const ROLE_KEY = 'lung_diagnosis_role';

export const setToken = (token) => {
  localStorage.setItem(TOKEN_KEY, token);
};

export const getToken = () => {
  return localStorage.getItem(TOKEN_KEY);
};

export const removeToken = () => {
  localStorage.removeItem(TOKEN_KEY);
};

export const setRole = (role) => {
  localStorage.setItem(ROLE_KEY, role);
};

export const getRole = () => {
  return localStorage.getItem(ROLE_KEY);
};

export const removeRole = () => {
  localStorage.removeItem(ROLE_KEY);
};

export const isAuthenticated = () => {
  return !!getToken();
};

export const logoutUser = () => {
  removeToken();
  removeRole();
  window.location.href = '/login';
};
