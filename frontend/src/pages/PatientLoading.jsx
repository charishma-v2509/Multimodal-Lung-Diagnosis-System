import React, { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Loader2 } from 'lucide-react';
import './PatientLoading.css';

const PatientLoading = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const aiResult = location.state?.aiResult || "Normal"; // fallback

  useEffect(() => {
    // Keep some UI waiting time even if API returned fast
    const timer = setTimeout(() => {
      navigate('/patient/result', { state: { aiResult } });
    }, 2500);

    return () => clearTimeout(timer);
  }, [navigate, aiResult]);

  return (
    <div className="loading-page animate-fade-in">
      <div className="loading-content">
        <div className="spinner-container">
          <Loader2 className="spinner-icon" size={80} />
          <div className="pulse-ring"></div>
        </div>
        <h2>AI Analysis in Progress</h2>
        <p className="loading-text">
          Analyzing X-ray and medical report using our advanced neural networks...
        </p>
        
        <div className="progress-bar-container mt-8">
          <div className="progress-bar-fill"></div>
        </div>
        
        <div className="loading-steps mt-6">
          <div className="step active">Extracting imaging features...</div>
          <div className="step">Cross-referencing symptom data...</div>
          <div className="step">Generating diagnostic report...</div>
        </div>
      </div>
    </div>
  );
};

export default PatientLoading;
