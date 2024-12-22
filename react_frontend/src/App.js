import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'; // Add Navigate
import Login from './pages/Login';
import Register from './pages/Register';
import StudyDashboard from './pages/StudyDashboard';
import PingTemplateDashboard from './pages/PingTemplateDashboard';
import PrivateRoute from './components/PrivateRoute';

function App() {
  return (
    <Router>
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Protected routes */}
        <Route
          path="/studies"
          element={
            <PrivateRoute>
              <StudyDashboard />
            </PrivateRoute>
          }
        />
        <Route
          path="/studies/:studyId/pingtemplates"
          element={
            <PrivateRoute>
              <PingTemplateDashboard />
            </PrivateRoute>
          }
        />

        {/* Catch-all route */}
        <Route path="*" element={<Navigate to="/studies" />} />
      </Routes>
    </Router>
  );
}

export default App;