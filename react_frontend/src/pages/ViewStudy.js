import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import StudyNav from '../components/StudyNav';
import axios from '../api/axios';

function ViewStudy() {
  const { studyId } = useParams();
  const navigate = useNavigate();

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
      <h1>Study: {study.internal_name}</h1>
      <StudyNav studyId={studyId} />
      {/* Display some basic details about the study */}
      <section style={{ marginBottom: '2rem' }}>
        <h2>Overview</h2>
        <p><strong>Public Name:</strong> {study.public_name}</p>
        <p><strong>Internal Name:</strong> {study.internal_name}</p>
        <p><strong>Contact Message:</strong> {study.contact_message}</p>
        <p><strong>Signup Code:</strong> {study.code}</p>
      </section>

    </div>
  );
}

export default ViewStudy;