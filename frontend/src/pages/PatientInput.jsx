import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import { UploadCloud, FileText, Image as ImageIcon, ArrowLeft } from 'lucide-react';
import Card from '../components/Card';
import Button from '../components/Button';
import './PatientInput.css';

const PatientInput = () => {
  const navigate = useNavigate();
  const [symptoms, setSymptoms] = useState('');
  const [impression, setImpression] = useState('');
  const [xrayFile, setXrayFile] = useState(null);
  const [xrayPreview, setXrayPreview] = useState(null);
  const [vitals, setVitals] = useState({
    oxygen: '',
    heart_rate: '',
    temperature: '',
    respiratory_rate: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleXrayChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setXrayFile(file);
      setXrayPreview(URL.createObjectURL(file));
    }
  };

  const handleVitalsChange = (e) => {
    const { id, value } = e.target;
    setVitals(prev => ({
      ...prev,
      [id]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      // Prepare data for the backend
      const formData = new FormData();
      formData.append('symptoms', symptoms);
      formData.append('impression', impression);
      formData.append('oxygen', vitals.oxygen);
      formData.append('heart_rate', vitals.heart_rate);
      formData.append('temperature', vitals.temperature);
      formData.append('respiratory_rate', vitals.respiratory_rate);
      formData.append('image', xrayFile);
      
      const response = await api.post('/patient/complete-diagnosis', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      navigate('/patient/loading', { 
        state: { aiResult: response.data } 
      });

    } catch (error) {
      console.error("Error submitting patient data:", error);
      alert("There was an error processing your request. Please ensure the backend is running at http://localhost:8000");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="page-container animate-fade-in">
      <div className="page-header">
        <button className="back-btn" onClick={() => navigate('/')}>
          <ArrowLeft size={20} />
          Back to Home
        </button>
        <h2>Patient Medical Assessment</h2>
        <p className="subtitle">Please provide your medical information for AI screening.</p>
      </div>

      <Card className="form-card">
        <form onSubmit={handleSubmit} className="patient-form">
          
          {/* Section 1 — Clinical Description */}
          <div className="form-section">
            <h3 className="section-title">Section 1 — Clinical Description</h3>
            <div className="input-group">
              <label className="input-label" htmlFor="symptoms">Symptoms</label>
              <textarea 
                id="symptoms"
                className="input-field" 
                placeholder="Cough for 2 days, fever, chest pain"
                value={symptoms}
                onChange={(e) => setSymptoms(e.target.value)}
                required
              />
            </div>
            <div className="input-group">
              <label className="input-label" htmlFor="impression">Doctor Impression</label>
              <textarea 
                id="impression"
                className="input-field" 
                placeholder="Possible respiratory infection"
                value={impression}
                onChange={(e) => setImpression(e.target.value)}
                required
              />
            </div>
          </div>

          {/* Section 2 — X-ray Upload */}
          <div className="form-section">
            <h3 className="section-title">Section 2 — X-ray Upload</h3>
            <div className="upload-container">
              <input 
                type="file" 
                id="xray-upload" 
                accept="image/*" 
                className="hidden-input"
                onChange={handleXrayChange}
                required
              />
              <label htmlFor="xray-upload" className="upload-box">
                {xrayPreview ? (
                  <div className="preview-container">
                    <img src={xrayPreview} alt="X-Ray Preview" className="image-preview" />
                    <div className="overlay">
                      <UploadCloud size={24} />
                      <span>Change Image</span>
                    </div>
                  </div>
                ) : (
                  <div className="upload-prompt">
                    <ImageIcon size={48} className="upload-icon text-muted" />
                    <span className="upload-text">Upload Chest X-Ray Image</span>
                    <span className="upload-subtext">JPEG, PNG or DICOM</span>
                  </div>
                )}
              </label>
            </div>
          </div>

          {/* Section 3 — Vitals */}
          <div className="form-section no-border">
            <h3 className="section-title">Section 3 — Vitals</h3>
            <div className="vitals-grid">
              <div className="input-group">
                <label className="input-label" htmlFor="oxygen">Oxygen</label>
                <input 
                  type="number"
                  id="oxygen"
                  className="input-field"
                  placeholder="SpO₂ percentage"
                  value={vitals.oxygen}
                  onChange={handleVitalsChange}
                  required
                />
              </div>
              <div className="input-group">
                <label className="input-label" htmlFor="heart_rate">Heart Rate</label>
                <input 
                  type="number"
                  id="heart_rate"
                  className="input-field"
                  placeholder="beats per minute"
                  value={vitals.heart_rate}
                  onChange={handleVitalsChange}
                  required
                />
              </div>
              <div className="input-group">
                <label className="input-label" htmlFor="temperature">Temperature</label>
                <input 
                  type="number"
                  step="0.1"
                  id="temperature"
                  className="input-field"
                  placeholder="body temperature"
                  value={vitals.temperature}
                  onChange={handleVitalsChange}
                  required
                />
              </div>
              <div className="input-group">
                <label className="input-label" htmlFor="respiratory_rate">Respiratory Rate</label>
                <input 
                  type="number"
                  id="respiratory_rate"
                  className="input-field"
                  placeholder="breaths per minute"
                  value={vitals.respiratory_rate}
                  onChange={handleVitalsChange}
                  required
                />
              </div>
            </div>
          </div>

          <div className="form-actions mt-8">
            <Button 
              type="submit" 
              variant="primary" 
              size="lg" 
              className="w-full"
              disabled={!symptoms || !impression || !xrayFile || !vitals.oxygen || !vitals.heart_rate || !vitals.temperature || !vitals.respiratory_rate || isSubmitting}
            >
              {isSubmitting ? 'Processing...' : 'Analyze Medical Data'}
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
};

export default PatientInput;
