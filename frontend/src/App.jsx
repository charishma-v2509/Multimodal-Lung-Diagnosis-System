import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import Login from './pages/Login';
import Register from './pages/Register';
import PatientHome from './pages/PatientHome';
import DoctorHome from './pages/DoctorHome';
import PatientInput from './pages/PatientInput';
import PatientLoading from './pages/PatientLoading';
import PatientResult from './pages/PatientResult';
import DoctorUpload from './pages/DoctorUpload';
import DoctorDashboard from './pages/DoctorDashboard';
import DoctorCaseReview from './pages/DoctorCaseReview';
import { isAuthenticated, getRole, logoutUser } from './utils/auth';
import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

const PrivateRoute = ({ children, allowedRole }) => {
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }
  if (allowedRole && getRole() !== allowedRole) {
    // Redirect securely back based on their real role
    return <Navigate to={getRole() === 'doctor' ? '/doctor/home' : '/patient/home'} replace />;
  }
  return children;
};

const SessionManager = () => {
  const location = useLocation();
  const TIMEOUT_DURATION = 15 * 60 * 1000; // 15 minutes in milliseconds

  useEffect(() => {
    if (!isAuthenticated()) return;

    const logout = () => {
      logoutUser();
      alert("Session expired due to inactivity. Please login again.");
    };

    const timer = setTimeout(logout, TIMEOUT_DURATION);

    return () => clearTimeout(timer);
  }, [location.pathname]);

  return null;
};

// Also protect the root paths if logged in already (e.g if user manually goes to /login but is logged in)
const PublicRoute = ({ children }) => {
  if (isAuthenticated()) {
    return <Navigate to={getRole() === 'doctor' ? '/doctor/home' : '/patient/home'} replace />;
  }
  return children;
};

function App() {
  return (
    <BrowserRouter>
      <SessionManager />
      <div className="app-container">
        <main className="main-content">
          <Routes>
            <Route path="/" element={<PublicRoute><LandingPage /></PublicRoute>} />
            <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
            <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />
            
            {/* Patient Routes */}
            <Route path="/patient/home" element={<PrivateRoute allowedRole="patient"><PatientHome /></PrivateRoute>} />
            <Route path="/patient/input" element={<PrivateRoute allowedRole="patient"><PatientInput /></PrivateRoute>} />
            <Route path="/patient/loading" element={<PrivateRoute allowedRole="patient"><PatientLoading /></PrivateRoute>} />
            <Route path="/patient/result" element={<PrivateRoute allowedRole="patient"><PatientResult /></PrivateRoute>} />
            
            {/* Doctor Routes */}
            <Route path="/doctor/home" element={<PrivateRoute allowedRole="doctor"><DoctorHome /></PrivateRoute>} />
            <Route path="/doctor/upload" element={<PrivateRoute allowedRole="doctor"><DoctorUpload /></PrivateRoute>} />
            <Route path="/doctor/dashboard" element={<PrivateRoute allowedRole="doctor"><DoctorDashboard /></PrivateRoute>} />
            <Route path="/doctor/review/:id" element={<PrivateRoute allowedRole="doctor"><DoctorCaseReview /></PrivateRoute>} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
