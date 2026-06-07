import React from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../components/Card';
import Button from '../components/Button';
import { Activity } from 'lucide-react';

const LandingPage = () => {
  const navigate = useNavigate();

  return (
    <div className="page-container animate-fade-in text-center" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '80vh'}}>
      <Activity size={64} className="text-primary mb-6" style={{ color: 'var(--primary)' }}/>
      <h1 style={{ fontSize: '3rem', marginBottom: '1rem', color: 'var(--primary)' }}>Multimodal Lung Diagnosis System</h1>
      <p className="subtitle" style={{ fontSize: '1.25rem', color: 'var(--text-muted)', maxWidth: '600px', margin: '0 auto 3rem auto' }}>
        Advanced AI-powered medical screening combining clinical indicators, vitals, and chest X-rays to aid doctors and patients with real-time diagnostic insights.
      </p>

      <Card style={{ padding: '2rem', width: '100%', maxWidth: '400px' }} className="glass-panel">
        <h3 className="section-title mb-4">Access the System</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <Button variant="primary" size="lg" className="w-full" onClick={() => navigate('/login')}>
            Login
          </Button>
          <Button variant="secondary" size="lg" className="w-full" onClick={() => navigate('/register')} style={{ background: 'var(--border)', color: 'var(--text-main)' }}>
            Register New Account
          </Button>
        </div>
      </Card>
    </div>
  );
};

export default LandingPage;
