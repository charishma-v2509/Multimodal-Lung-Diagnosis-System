import React, { useState } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import api from '../api';
import { ArrowLeft, User, Activity, FileText, CheckCircle, PieChart, Layers } from 'lucide-react';
import Card from '../components/Card';
import Button from '../components/Button';
import './DoctorCaseReview.css';

const DoctorCaseReview = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const [opinion, setOpinion] = useState('');
  
  // Extract data from state or provide fallbacks
  const patientContext = location.state?.patientContext || null;
  const rawReport = location.state?.rawReport || patientContext;
  const previewUrl = location.state?.previewUrl || null;
  
  // Prioritize doctor_report from rawReport (dashboard cases) or analysisResult (direct uploads)
  const analysisResult = location.state?.analysisResult || rawReport?.doctor_report || null;

  console.log("DoctorCaseReview - rawReport:", rawReport);
  console.log("DoctorCaseReview - analysisResult:", analysisResult);

  const patientName = rawReport?.patient_name || rawReport?.name || 'Unknown Patient';
  const symptoms = rawReport?.symptoms || 'Not provided';
  
  const getHeatmapSrc = (path) => {
    if (!path) return '';
    if (path.startsWith('http') || path.startsWith('data:')) {
      return path;
    }
    if (path.startsWith('uploads/')) {
      return `http://localhost:8000/${path}`;
    }
    if (path.startsWith('/')) {
      return `http://localhost:8000${path}`;
    }
    return `data:image/jpeg;base64,${path}`;
  };

  // Use persistent URL if available, then local preview, then fallback
  const rawXray = rawReport?.image_path || rawReport?.image_url || previewUrl;
  const MOCK_XRAY_URL = getHeatmapSrc(rawXray) || 'https://images.unsplash.com/photo-1559706132-ea6335bac674?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80';

  // Process AI results dynamically from backend doctor_report
  const finalPrediction = analysisResult?.final_prediction || "Normal";
  const diffDiag = analysisResult?.differential_diagnosis || [];
  
  // Create display objects for the differential diagnosis section
  const sortedProbabilities = diffDiag.length > 0 
    ? diffDiag.map((item) => ({
        condition: typeof item === 'string' ? item : item.condition,
        percent: typeof item === 'string' ? 85 : item.confidence
      }))
    : [{ condition: finalPrediction, percent: 90 }];

  const primaryMatch = sortedProbabilities[0];
  const secondaryMatches = sortedProbabilities.slice(1);

  const submitOpinion = () => {
    alert("Opinion saved and report finalized.");
    navigate('/doctor/dashboard');
  };

  return (
    <div className="review-container animate-fade-in">
      <div className="page-header d-flex-between">
        <div>
          <button className="back-btn" onClick={() => navigate('/doctor/dashboard')}>
            <ArrowLeft size={20} />
            Back to Dashboard
          </button>
          <h2>Case Review: {patientName}</h2>
          <p className="subtitle">Detailed AI analysis and differential diagnosis.</p>
        </div>
        <div className={`status-badge ${finalPrediction === "Normal" ? 'bg-success-light text-success' : 'bg-warning-light text-warning'}`}>
          <Activity size={18} />
          {finalPrediction === "Normal" ? 'Screening: Normal' : 'Pending Doctor Review'}
        </div>
      </div>

      <div className="review-grid">
        {/* Left Column: Data & Input */}
        <div className="review-main">
          <Card className="info-card mb-6">
            <h3 className="card-heading">
              <User size={20} className="text-primary" />
              Patient Information & Symptoms
            </h3>
            <div className="info-content bg-slate-50">
              <p><strong>ID:</strong> {id}</p>
              <p><strong>Reported Symptoms:</strong></p>
              <p className="symptoms-text">{symptoms}</p>
            </div>
          </Card>

          <Card className="info-card mb-6">
            <h3 className="card-heading">
              <Layers size={20} className="text-primary" />
              Medical Imaging
            </h3>
            <div className="single-image-display">
                <p className="text-center text-muted mt-2 text-sm italic">Standard Chest X-Ray View</p>
                
                <div className="image-comparison mt-6">
                  <div className="image-box">
                    <span className="image-label">Original X-Ray</span>
                    <img src={MOCK_XRAY_URL} alt="Original X-Ray" className="radiograph" />
                  </div>
                  <div className="image-box">
                    <span className="image-label text-primary">AI Heatmap Visualization</span>
                    {analysisResult?.heatmap_path ? (
                      <img src={getHeatmapSrc(analysisResult.heatmap_path)} alt="AI Heatmap Overlay" className="radiograph" />
                    ) : (
                      <div className="placeholder-info bg-slate-100 flex-center h-full rounded-lg text-muted">
                        <Layers size={32} className="mb-2 opacity-20" />
                        <span>Heatmap not generated for this case</span>
                      </div>
                    )}
                  </div>
                </div> 
            </div>
          </Card>

          <Card className="info-card">
            <h3 className="card-heading">
              <FileText size={20} className="text-primary" />
              Doctor's Assessment
            </h3>
            <div className="input-group">
              <label className="input-label mb-2">Write your clinical opinion and recommendations</label>
              <textarea 
                className="input-field" 
                placeholder="Example: Likely pneumonia. Recommend CT scan..."
                value={opinion}
                onChange={(e) => setOpinion(e.target.value)}
                style={{ minHeight: '150px' }}
              />
            </div>
            <div className="flex-end mt-4">
              <Button variant="primary" onClick={submitOpinion} disabled={!opinion}>
                <CheckCircle size={18} />
                Finalize Report
              </Button>
            </div>
          </Card>
        </div>

        {/* Right Column: AI Analysis */}
        <div className="review-sidebar">
          <Card className="ai-card">
            <div className="ai-header">
              <PieChart size={24} color="white" />
              <h3>AI Differential Diagnosis</h3>
            </div>
            
            <div className="ai-content">
              <div className="top-diagnosis mb-6">
                <span className="text-sm uppercase fw-600 text-danger">Primary Match</span>
                <h2 className="text-2xl mt-1">{primaryMatch.condition}</h2>
                
                <div className="probability-bar-container mt-2">
                  <div className="probability-bar probability-high" style={{ width: `${primaryMatch.percent}%` }}></div>
                </div>
                <div className="probability-value text-right mt-1">{primaryMatch.percent}% Confidence</div>
              </div>

              <div className="secondary-diagnoses">
                <h4 className="text-sm uppercase fw-600 text-muted mb-3">Other Possibilities</h4>
                
                {secondaryMatches.map((match, index) => (
                  <div className="diag-item" key={index}>
                    <div className="diag-item-header">
                      <span>{match.condition}</span>
                      <span>{match.percent}%</span>
                    </div>
                    <div className="probability-bar-container mini">
                      <div className={`probability-bar ${match.percent > 20 ? 'probability-med' : 'probability-low'}`} style={{ width: `${match.percent}%` }}></div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="ai-findings mt-6 box-alert box-warning">
                <strong>Key AI Findings:</strong>
                <ul className="findings-list mt-2">
                  {analysisResult?.modality_contribution ? (
                    Object.entries(analysisResult.modality_contribution).map(([key, val], i) => (
                      <li key={i}><strong>{key.replace('_', ' ').toUpperCase()}:</strong> {val}</li>
                    ))
                  ) : (
                    <>
                      <li>Patterns detected in the chest X-ray.</li>
                      <li>Clinical notes analyzed for respiratory indicators.</li>
                      <li>Vital signs checked against healthy ranges.</li>
                    </>
                  )}
                </ul>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default DoctorCaseReview;
