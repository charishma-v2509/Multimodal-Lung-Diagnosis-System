import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../components/Card';
import Button from '../components/Button';
import { register } from '../services/authService';

const Register = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    role: 'patient'
  });
  const [errorMsg, setErrorMsg] = useState('');
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => setFormData(prev => ({ ...prev, [e.target.id]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    setLoading(true);

    try {
      await register(formData.name, formData.email, formData.password, formData.role);
      setSuccess(true);
      setTimeout(() => navigate('/login'), 2000);
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'Failed to register');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container animate-fade-in" style={{ display: 'flex', justifyContent: 'center', marginTop: '4rem' }}>
      <Card style={{ width: '100%', maxWidth: '450px', padding: '2rem' }}>
        <h2 className="text-center mb-6">Register</h2>
        
        {errorMsg && <div style={{ background: 'var(--danger)', color: 'white', padding: '0.75rem', borderRadius: 'var(--radius-md)', marginBottom: '1rem' }}>{errorMsg}</div>}
        {success && <div style={{ background: 'var(--success)', color: 'white', padding: '0.75rem', borderRadius: 'var(--radius-md)', marginBottom: '1rem' }}>Registration successful! Redirecting...</div>}

        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <label className="input-label" htmlFor="name">Full Name</label>
            <input 
              id="name" type="text" className="input-field" required
              value={formData.name} onChange={handleChange} placeholder="John Doe"
            />
          </div>

          <div className="input-group">
            <label className="input-label" htmlFor="email">Email Address</label>
            <input 
              id="email" type="email" className="input-field" required
              value={formData.email} onChange={handleChange} placeholder="name@example.com"
            />
          </div>

          <div className="input-group">
            <label className="input-label" htmlFor="password">Password</label>
            <input 
              id="password" type="password" className="input-field" required minLength={4}
              value={formData.password} onChange={handleChange} placeholder="••••••••"
            />
          </div>

          <div className="input-group">
            <label className="input-label" htmlFor="role">Role</label>
            <select id="role" className="input-field" value={formData.role} onChange={handleChange}>
              <option value="patient">Patient</option>
              <option value="doctor">Doctor</option>
            </select>
          </div>

          <Button type="submit" variant="primary" size="lg" className="w-full mt-4" disabled={loading || success}>
            {loading ? 'Registering...' : 'Create Account'}
          </Button>

          <p className="text-center mt-6 text-muted" style={{ color: 'var(--text-muted)' }}>
            Already have an account? <span style={{ color: 'var(--primary)', cursor: 'pointer', fontWeight: '500' }} onClick={() => navigate('/login')}>Login here</span>
          </p>
        </form>
      </Card>
    </div>
  );
};

export default Register;
