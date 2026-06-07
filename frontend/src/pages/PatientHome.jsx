import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../components/Card';
import Button from '../components/Button';
import api from '../api';
import { logoutUser } from '../utils/auth';

const PatientHome = () => {
  const navigate = useNavigate();
  const [userName, setUserName] = useState('');

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const response = await api.get('/me');
        setUserName(response.data.name);
      } catch (err) {
        console.error('Failed to fetch user', err);
      }
    };
    fetchUser();
  }, []);

  return (
    <div className="page-container animate-fade-in" style={{ padding: '2rem 1rem' }}>
      <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
        <h1 style={{ color: 'var(--primary)', fontSize: '2.5rem' }}>Multimodal Lung Diagnosis System</h1>
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h2>Welcome, {userName || 'Patient'}</h2>
        <Button variant="secondary" onClick={logoutUser} style={{ background: 'var(--border)' }}>Logout</Button>
      </div>

      <div style={{ display: 'flex', gap: '2rem', justifyContent: 'center', marginTop: '4rem' }}>
        <Card style={{ width: '100%', maxWidth: '350px', padding: '2rem', textAlign: 'center', cursor: 'pointer' }} onClick={() => navigate('/patient/input')}>
          <h3 style={{ color: 'var(--primary)', marginBottom: '1rem' }}>Upload Medical Case</h3>
          <p style={{ color: 'var(--text-muted)' }}>Start a new AI-assisted diagnosis session by uploading clinical symptoms, vitals, and chest X-rays.</p>
          <Button variant="primary" className="w-full mt-6" onClick={(e) => { e.stopPropagation(); navigate('/patient/input'); }}>
            Start Diagnosis
          </Button>
        </Card>
      </div>
    </div>
  );
};

export default PatientHome;
