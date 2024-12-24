import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Register from './pages/Register';
import StudyDashboard from './pages/StudyDashboard';
import PingTemplateDashboard from './pages/PingTemplateDashboard';
import StudyEnroll from './pages/StudyEnroll'; 
import PingDashboard from './pages/PingDashboard';
import ViewStudy from './pages/ViewStudy';
import PrivateRoute from './components/PrivateRoute';
import NavBar from './components/NavBar';

function App() {
  return (
    <Router>
      <div>
        <NavBar />
      <main>
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/enroll/:signup_code" element={<StudyEnroll />} />

        {/* Protected routes */}
        <Route path="/studies"
          element={
            <PrivateRoute>
              <StudyDashboard />
            </PrivateRoute>
          }
        />
        <Route path="/studies/:studyId"
          element={
            <PrivateRoute>
              <ViewStudy />
            </PrivateRoute>
          }
        />
        <Route path="/studies/:studyId/ping_templates"
          element={
            <PrivateRoute>
              <PingTemplateDashboard />
            </PrivateRoute>
          }
        />
        <Route path="/studies/:studyId/pings"
          element={
            <PrivateRoute>
              <PingDashboard />
            </PrivateRoute>
          }
        />
        <Route path="/studies/:studyId/participants"
          element={
            <PrivateRoute>
              <ParticipantDashboard />
            </PrivateRoute>
          }
        />


        {/* Catch-all route */}
        <Route path="*" element={<Navigate to="/studies" />} />
      </Routes>
      </main>
      </div>
    </Router>
  );
}

export default App;