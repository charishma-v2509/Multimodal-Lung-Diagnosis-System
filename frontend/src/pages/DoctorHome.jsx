import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../components/Card';
import Button from '../components/Button';
import api from '../api';
import { logoutUser } from '../utils/auth';

const DoctorHome = () => {
  const navigate = useNavigate();
  const [docName, setDocName] = useState('');

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const response = await api.get('/me');
        setDocName(response.data.name);
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
        <h2>Welcome Dr. {docName || 'Doctor'}</h2>
        <Button variant="secondary" onClick={logoutUser} style={{ background: 'var(--border)' }}>Logout</Button>
      </div>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '2rem', justifyContent: 'center', marginTop: '4rem' }}>
        <Card style={{ flex: '1 1 300px', maxWidth: '350px', padding: '2rem', textAlign: 'center', cursor: 'pointer' }} onClick={() => navigate('/doctor/upload')}>
          <h3 style={{ color: 'var(--primary)', marginBottom: '1rem' }}>Upload Patient Case</h3>
          <p style={{ color: 'var(--text-muted)' }}>Quickly upload a patient's medical records to get AI-aided prescreening insights.</p>
          <Button variant="primary" className="w-full mt-6" onClick={(e) => { e.stopPropagation(); navigate('/doctor/upload'); }}>
            New Case
          </Button>
        </Card>

        <Card style={{ flex: '1 1 300px', maxWidth: '350px', padding: '2rem', textAlign: 'center', cursor: 'pointer' }} onClick={() => navigate('/doctor/dashboard')}>
          <h3 style={{ color: 'var(--secondary)', marginBottom: '1rem' }}>View Dashboard</h3>
          <p style={{ color: 'var(--text-muted)' }}>Review uploaded patient cases, analyze results, and confidently add clinical notes.</p>
          <Button variant="secondary" className="w-full mt-6" onClick={(e) => { e.stopPropagation(); navigate('/doctor/dashboard'); }}>
            Open Dashboard
          </Button>
        </Card>
      </div>
    </div>
  );
};

export default DoctorHome;
