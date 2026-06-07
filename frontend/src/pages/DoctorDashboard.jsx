import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import { Search, ChevronRight, Activity, Clock, AlertTriangle, ArrowLeft } from 'lucide-react';
import Card from '../components/Card';
import './DoctorDashboard.css';


const DoctorDashboard = () => {
  const navigate = useNavigate();
  const [cases, setCases] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchCases = async () => {
      try {
        const response = await api.get('/reports');
        // Map backend report format to frontend expected format
        const formattedCases = response.data.map(report => {
          const analysis = report.doctor_report || report.patient_report;
          
          // Calculate severity based on new rules
          const calculateSeverity = (aiRes) => {
            if (!aiRes) return "Mild";
            
            const redFlags = aiRes.clinical_red_flags || [];
            const modContrib = aiRes.modality_contribution || {};
            const symptomModel = modContrib.symptom_model || "";
            
            if (symptomModel === "Critical Risk" || (Array.isArray(redFlags) && redFlags.length > 0)) {
              return "Severe";
            }
            
            const abnormalCount = Object.values(modContrib).filter(val => 
              val !== "Normal" && val !== "No Risk" && val !== "Low Risk"
            ).length;
            
            if (abnormalCount >= 2) {
              return "Moderate";
            }
            
            return "Mild";
          };

          const severity = calculateSeverity(analysis);

          return {
            id: report.id.toString(),
            name: report.patient_name || report.name || 'Unknown Patient',
            result: report.prediction?.disease || report.final_result || 'Pending AI Analysis',
            severity: severity,
            time: 'Just now',
            date: 'Today',
            rawReport: report
          };
        });
        setCases(formattedCases.reverse()); // Newest first
      } catch (error) {
        console.error("Error fetching patient reports:", error);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchCases();
  }, []);

  const getSeverityBadge = (severity) => {
    switch(severity) {
      case 'Mild': return <span className="badge badge-success">MILD</span>;
      case 'Moderate': return <span className="badge badge-warning">MODERATE</span>;
      case 'Severe': return <span className="badge badge-danger">SEVERE</span>;
      default: return <span className="badge badge-success">MILD</span>;
    }
  };

  const pendingCount = cases.length;
  const criticalCount = cases.filter(c => c.severity === 'Severe').length;

  return (
    <div className="dashboard-container animate-fade-in">
      <div className="page-header d-flex-between">
        <div>
          <button className="back-btn" onClick={() => navigate('/')}>
            <ArrowLeft size={20} />
            Home
          </button>
          <h2>Doctor Dashboard</h2>
          <p className="subtitle">Review pending patient cases and AI preliminary analyses.</p>
        </div>
        <div className="header-stats">
          <Card className="stat-card">
            <Activity className="stat-icon" size={24} color="var(--primary)" />
            <div className="stat-info">
              <span className="stat-value">{pendingCount}</span>
              <span className="stat-label">Pending</span>
            </div>
          </Card>
          <Card className="stat-card">
            <AlertTriangle className="stat-icon" size={24} color="var(--danger)" />
            <div className="stat-info">
              <span className="stat-value">{criticalCount}</span>
              <span className="stat-label">Critical</span>
            </div>
          </Card>
        </div>
      </div>

      <div className="search-bar-container">
        <div className="search-input-wrapper">
          <Search className="search-icon" size={20} />
          <input 
            type="text" 
            placeholder="Search patient name, ID, or condition..." 
            className="search-input"
          />
        </div>
      </div>

      <div className="cases-list">
        <h3>Recent Submissions</h3>
        {isLoading ? (
          <p>Loading patient cases...</p>
        ) : cases.length === 0 ? (
          <p className="text-muted mt-4">No patient cases found.</p>
        ) : (
          <div className="cases-grid">
            {cases.map((patient) => (
            <Card 
              key={patient.id} 
              className="case-card clickable"
              hoverable
              onClick={() => navigate(`/doctor/review/${patient.id}`, { state: { rawReport: patient.rawReport } })}
            >
              <div className="case-main">
                <div className="case-header">
                  <h4 className="patient-name">{patient.name}</h4>
                  {getSeverityBadge(patient.severity)}
                </div>
                <p className="case-result">
                  <strong>Prediction:</strong> {patient.result}
                </p>
                <div className="case-footer">
                  <span className="case-time">
                    <Clock size={14} className="time-icon" />
                    {patient.time}
                  </span>
                </div>
              </div>
              <div className="case-action">
                <ChevronRight size={24} color="var(--text-muted)" />
              </div>
            </Card>
          ))}
        </div>
        )}
      </div>
    </div>
  );
};

export default DoctorDashboard;
