import api from '../api';
import { setToken, setRole, removeToken, removeRole } from '../utils/auth';

export const login = async (email, password) => {
  // Using Form Data or JSON depending on backend setup. Backend expects JSON schema: UserLogin
  const response = await api.post('/login', { email, password });
  const { access_token, role } = response.data;
  
  if (access_token) {
    setToken(access_token);
    setRole(role);
  }
  return response.data;
};

export const register = async (name, email, password, role) => {
  const response = await api.post('/register', { name, email, password, role });
  return response.data;
};

export const logout = () => {
  removeToken();
  removeRole();
};
