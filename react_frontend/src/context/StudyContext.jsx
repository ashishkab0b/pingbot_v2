// src/context/StudyContext.js
import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from '../api/axios'; 

// Create a context to hold the study object
const StudyContext = createContext();

// Provider component; supply `studyId` as a prop from a parent (e.g., in a route).
export const StudyProvider = ({ studyId, children }) => {
  const [study, setStudy] = useState(null);

  useEffect(() => {
    // Helper function to fetch the study details
    const fetchStudy = async () => {
      try {
        const response = await axios.get(`/studies/${studyId}`);
        // The response.data should include { ..., role: "..."}
        setStudy(response.data);
      } catch (err) {
        console.error('Error fetching study:', err);
        setStudy(null); // or keep it as null to indicate error/no access
      }
    };

    if (studyId) {
      fetchStudy();
    } else {
      // If studyId is empty or missing, reset to null
      setStudy(null);
    }
  }, [studyId]);

  // The 'study' object here includes role, code, internal_name, etc.
  return (
    <StudyContext.Provider value={study}>
      {children}
    </StudyContext.Provider>
  );
};

// Export a simple hook to get the context
export const useStudy = () => {
  return useContext(StudyContext);
};