import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../components/Card';
import Button from '../components/Button';
import { login } from '../services/authService';

const Login = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    setLoading(true);

    try {
      const data = await login(email, password);
      if (data.role === 'patient') navigate('/patient/home');
      else if (data.role === 'doctor') navigate('/doctor/home');
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'Failed to login');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container animate-fade-in" style={{ display: 'flex', justifyContent: 'center', marginTop: '4rem' }}>
      <Card style={{ width: '100%', maxWidth: '450px', padding: '2rem' }}>
        <h2 className="text-center mb-6">Login</h2>
        
        {errorMsg && <div style={{ background: 'var(--danger)', color: 'white', padding: '0.75rem', borderRadius: 'var(--radius-md)', marginBottom: '1rem' }}>{errorMsg}</div>}

        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <label className="input-label" htmlFor="email">Email Address</label>
            <input 
              id="email" type="email" className="input-field" required
              value={email} onChange={e => setEmail(e.target.value)}
              placeholder="name@example.com"
            />
          </div>

          <div className="input-group">
            <label className="input-label" htmlFor="password">Password</label>
            <input 
              id="password" type="password" className="input-field" required
              value={password} onChange={e => setPassword(e.target.value)}
              placeholder="••••••••"
            />
          </div>

          <Button type="submit" variant="primary" size="lg" className="w-full mt-4" disabled={loading}>
            {loading ? 'Logging in...' : 'Login'}
          </Button>

          <p className="text-center mt-6 text-muted" style={{ color: 'var(--text-muted)' }}>
            Don't have an account? <span style={{ color: 'var(--primary)', cursor: 'pointer', fontWeight: '500' }} onClick={() => navigate('/register')}>Register here</span>
          </p>
        </form>
      </Card>
    </div>
  );
};

export default Login;
