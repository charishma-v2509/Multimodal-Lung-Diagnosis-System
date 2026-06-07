import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import api from '../api';
import { Download, Send, AlertTriangle, CheckCircle, Info, Home } from 'lucide-react';
import Card from '../components/Card';
import Button from '../components/Button';
import './PatientResult.css';

const PatientResult = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const aiResult = location.state?.aiResult;
  
  const [doctors, setDoctors] = useState([]);
  const [showDoctorSelect, setShowDoctorSelect] = useState(false);
  const [selectedDoctor, setSelectedDoctor] = useState('');
  const [isAssigned, setIsAssigned] = useState(false);
  const [isAssigning, setIsAssigning] = useState(false);

  useEffect(() => {
    const fetchDoctors = async () => {
      try {
        const response = await api.get('/doctors');
        setDoctors(response.data);
      } catch (err) {
        console.error("Failed to fetch doctors:", err);
      }
    };
    fetchDoctors();
  }, []);
  
  // Calculate severity based on new rules
  const calculateSeverity = (aiRes) => {
    if (!aiRes) return "Mild";
    
    const redFlags = aiRes.clinical_red_flags || [];
    const modContrib = aiRes.modality_contribution || {};
    const symptomModel = modContrib.symptom_model || "";
    
    // Rule 1: Severe if symptom_model is Critical Risk or red flags exist
    if (symptomModel === "Critical Risk" || (Array.isArray(redFlags) && redFlags.length > 0)) {
      return "Severe";
    }
    
    // Rule 2: Moderate if two or more models are "Abnormal"
    // We consider anything not "Normal", "No Risk", or "Low Risk" as abnormal
    const abnormalCount = Object.values(modContrib).filter(val => 
      val !== "Normal" && val !== "No Risk" && val !== "Low Risk"
    ).length;
    
    if (abnormalCount >= 2) {
      return "Moderate";
    }
    
    return "Mild";
  };

  // Map backend response to UI display object
  const result = {
    condition: aiResult?.possible_condition_explanation || "No significant abnormalities detected",
    severity: calculateSeverity(aiResult), 
    explanation: aiResult?.recommended_next_steps || "The AI system detected no obvious signs of lung infection or abnormalities."
  };

  const getSeverityColor = (severity) => {
    switch(severity) {
      case 'Mild': return 'severity-mild';
      case 'Moderate': return 'severity-moderate';
      case 'Severe': return 'severity-severe';
      default: return 'severity-mild';
    }
  };

  const getSeverityIcon = (severity) => {
    switch(severity) {
      case 'Mild': return <CheckCircle size={32} />;
      case 'Moderate': return <Info size={32} />;
      case 'Severe': return <AlertTriangle size={32} />;
      default: return <Info size={32} />;
    }
  };

  const handleSendToDoctor = async () => {
    if (!showDoctorSelect) {
      setShowDoctorSelect(true);
      return;
    }
    
    if (!selectedDoctor) {
      alert("Please select a doctor from the list.");
      return;
    }

    setIsAssigning(true);
    try {
      await api.post('/assign-doctor', {
        report_id: aiResult.id,
        doctor_id: selectedDoctor
      });
      setIsAssigned(true);
      setShowDoctorSelect(false);
      alert("Report sent to the selected doctor successfully.");
    } catch (err) {
      console.error("Failed to assign doctor:", err);
      alert("Failed to send report. Please try again.");
    } finally {
      setIsAssigning(false);
    }
  };

  const handleDownloadPDF = () => {
    window.print();
  };

  return (
    <div className="page-container animate-fade-in">
      <div className="page-header text-center mb-6">
        <h2>AI Analysis Complete</h2>
        <p className="subtitle">Review your preliminary screening results below.</p>
      </div>

      <Card className={`result-card ${getSeverityColor(result.severity)}`}>
        <div className="severity-header">
          <div className="severity-icon">
            {getSeverityIcon(result.severity)}
          </div>
          <div className="severity-text-content">
            <span className="severity-label">Severity Level</span>
            <h3 className="severity-value">{result.severity}</h3>
          </div>
        </div>
        
        <div className="condition-section">
          <h4>Possible Condition:</h4>
          <p className="condition-title">{result.condition}</p>
        </div>

        <div className="explanation-section">
          <h4>AI Explanation:</h4>
          <p>{result.explanation}</p>
        </div>

        <div className="disclaimer">
          <strong>Disclaimer:</strong> This is an AI-assisted initial screening, not a definitive medical diagnosis. Always consult a healthcare professional.
        </div>
      </Card>

      <div className="action-buttons mt-6" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {showDoctorSelect && !isAssigned && (
          <div style={{ width: '100%', display: 'flex', gap: '1rem' }}>
            <select 
              value={selectedDoctor} 
              onChange={(e) => setSelectedDoctor(e.target.value)}
              style={{ flex: 1, padding: '0.75rem', borderRadius: '0.5rem', border: '1px solid var(--border)' }}
            >
              <option value="">-- Select a Doctor --</option>
              {doctors.map(doc => (
                <option key={doc.id} value={doc.id}>Dr. {doc.name.replace(/^Dr\.\s*/i, '')}</option>
              ))}
            </select>
            {doctors.length === 0 && <span style={{alignSelf: 'center', color: 'var(--text-muted)'}}>Loading...</span>}
          </div>
        )}
        <div style={{ display: 'flex', gap: '1rem', width: '100%' }}>
          <Button 
            variant="primary" 
            size="lg" 
            className="flex-1"
            onClick={handleSendToDoctor}
            disabled={isAssigned || isAssigning}
          >
            <Send size={20} />
            {isAssigned ? "Sent to Doctor" : (showDoctorSelect ? (isAssigning ? "Sending..." : "Confirm Send") : "Send Report to Doctor")}
          </Button>
          <Button 
            variant="outline" 
            size="lg" 
            className="flex-1"
            onClick={handleDownloadPDF}
          >
            <Download size={20} />
            Download AI Report (PDF)
          </Button>
        </div>
      </div>
      
      <div className="text-center mt-6">
        <Button variant="secondary" onClick={() => navigate('/')}>
          <Home size={20} />
          Return to Home
        </Button>
      </div>
    </div>
  );
};

export default PatientResult;
