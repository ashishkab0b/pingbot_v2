import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import StudyNav from '../components/StudyNav';
import axios from '../api/axios';
import { Typography } from '@mui/material';

function ViewStudy() {
  const { studyId } = useParams();

  const [study, setStudy] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch the study details
  useEffect(() => {
    fetchStudyDetail(studyId);
    // eslint-disable-next-line
  }, [studyId]);

  const fetchStudyDetail = async (id) => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`/studies/${id}`);
      setStudy(response.data);
    } catch (err) {
      console.error(err);
      setError('Error fetching study details');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <p>Loading study details...</p>;
  if (error) return <p style={{ color: 'red' }}>{error}</p>;
  if (!study) return <p>Study not found or you do not have access.</p>;

  return (
    <div style={{ margin: '2rem' }}>
      
      <Typography variant="h4" gutterBottom>
        Study: {study?.internal_name || 'Loading...'}
      </Typography>
      <StudyNav studyId={studyId} />
      {/* Display some basic details about the study */}
      <section style={{ marginBottom: '2rem' }}>
        
        {/* <Typography variant="h5" gutterBottom>
          Overview
        </Typography> */}
        <p><strong>Public Name:</strong> {study.public_name}</p>
        <p><strong>Internal Name:</strong> {study.internal_name}</p>
        <p><strong>Contact Message:</strong> {study.contact_message}</p>
        <p>
        <strong>Enrollment link: </strong>
        {`${process.env.REACT_APP_BASE_URL}/enroll/${study.code}?pid=`}
        <span style={{ color: 'red' }}>&lt;REPLACE_WITH_PARTICIPANT_ID&gt;</span>
      </p>
      </section>

    </div>
  );
}

export default ViewStudy;