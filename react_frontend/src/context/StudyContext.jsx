import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from '../api/axios'; 

const StudyContext = createContext();

export const StudyProvider = ({ studyId, children }) => {
  const [study, setStudy] = useState(null);

  useEffect(() => {
    const fetchStudy = async () => {
      try {
        const response = await axios.get(`/studies/${studyId}`);
        setStudy(response.data);
      } catch (err) {
        console.error('Error fetching study:', err);
        setStudy(null);
      }
    };

    if (studyId) fetchStudy();
  }, [studyId]);

  return (
    <StudyContext.Provider value={study}>
      {children}
    </StudyContext.Provider>
  );
};

export const useStudy = () => useContext(StudyContext);