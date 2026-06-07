import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Stethoscope, UserCircle } from 'lucide-react';
import Card from '../components/Card';
import Button from '../components/Button';
import './Home.css';

const Home = () => {
  const navigate = useNavigate();

  return (
    <div className="home-container animate-fade-in">
      <div className="home-header">
        <div className="logo-icon">
          <Stethoscope size={48} color="var(--primary)" />
        </div>
        <h1>Multimodal AI Lung Diagnosis System</h1>
        <p className="home-subtitle">
          Advanced artificial intelligence system that analyzes chest X-rays and medical reports 
          to assist in the early detection and screening of lung diseases.
        </p>
      </div>

      <div className="role-selection">
        <Card className="role-card" hoverable>
          <div className="role-icon-wrapper patient-icon bg-sky">
            <UserCircle size={64} />
          </div>
          <h2>Patient Mode</h2>
          <p>Provide your symptoms, X-ray images, and medical reports for an AI-assisted initial screening.</p>
          <Button 
            variant="primary" 
            className="w-full mt-4" 
            onClick={() => navigate('/patient/input')}
          >
            Start Screening
          </Button>
        </Card>

        <Card className="role-card" hoverable>
          <div className="role-icon-wrapper doctor-icon bg-teal">
            <Stethoscope size={64} />
          </div>
          <h2>Doctor Mode</h2>
          <p>Upload patient cases for advanced AI analysis or review existing patient submissions securely.</p>
          <div className="doctor-actions">
            <Button 
              variant="outline" 
              className="w-full mt-4 submit-btn" 
              onClick={() => navigate('/doctor/upload')}
            >
              Upload Case
            </Button>
            <Button 
              variant="primary" 
              className="w-full mt-4 submit-btn" 
              onClick={() => navigate('/doctor/dashboard')}
            >
              Doctor Dashboard
            </Button>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Home;
