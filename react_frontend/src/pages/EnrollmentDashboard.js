import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import StudyNav from '../components/StudyNav';
import { useStudy } from '../context/StudyContext';
import axios from '../api/axios';

function EnrollmentDashboard() {
  const { studyId } = useParams();
  const study = useStudy();

  // ------------------------------------------------
  // State
  // ------------------------------------------------
  const [participants, setParticipants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Pagination
  const [page, setPage] = useState(1);
  const [perPage] = useState(5);
  const [totalPages, setTotalPages] = useState(1);

  // Create form fields (matching enrollments table)
  // Required fields for enrollment: tz, study_pid
  const [tz, setTz] = useState('');
  const [studyPid, setStudyPid] = useState('');
  const [enrolled, setEnrolled] = useState(true);
  // Optional: start_date, etc.

  const [showCreateForm, setShowCreateForm] = useState(false);

  // ------------------------------------------------
  // Fetch participants on mount or page change
  // ------------------------------------------------
  useEffect(() => {
    if (studyId) {
      fetchParticipants(studyId, page, perPage);
    }
    // eslint-disable-next-line
  }, [studyId, page]);

  const fetchParticipants = async (studyId, currentPage, itemsPerPage) => {
    setLoading(true);
    setError(null);

    try {
      // GET /studies/<study_id>/enrollments
      const response = await axios.get(
        `/studies/${studyId}/enrollments?page=${currentPage}&per_page=${itemsPerPage}`
      );
      const { data, meta } = response.data;

      setParticipants(data);
      setPage(meta.page);
      setTotalPages(meta.pages);
    } catch (err) {
      console.error(err);
      setError('Error fetching participants.');
    } finally {
      setLoading(false);
    }
  };

  // ------------------------------------------------
  // Create new participant
  // ------------------------------------------------
  const handleCreateParticipant = async (e) => {
    e.preventDefault();

    try {
      await axios.post(`/studies/${studyId}/enrollments`, {
        tz,
        study_pid: studyPid,
        enrolled,
        // Optional: start_date
      });
      // Reset form
      setTz('');
      setStudyPid('');
      setEnrolled(true);

      setShowCreateForm(false);

      // Refresh the table
      fetchParticipants(studyId, page, perPage);
    } catch (err) {
      console.error(err);
      setError('Error creating participant.');
    }
  };

  // ------------------------------------------------
  // Simple pagination
  // ------------------------------------------------
  const handlePreviousPage = () => {
    if (page > 1) {
      setPage((prev) => prev - 1);
    }
  };

  const handleNextPage = () => {
    if (page < totalPages) {
      setPage((prev) => prev + 1);
    }
  };

  // ------------------------------------------------
  // Edge case if studyId is missing
  // ------------------------------------------------
  if (!studyId) {
    return <div>Error: Missing studyId in URL.</div>;
  }

  // ------------------------------------------------
  // Render
  // ------------------------------------------------
  return (
    <div style={{ margin: '2rem' }}>
      <StudyNav />
      <h1>Participants for {study?.internal_name || 'Loading...'}</h1>

      <button
        style={{ marginBottom: '1rem' }}
        onClick={() => setShowCreateForm(!showCreateForm)}
      >
        {showCreateForm ? 'Cancel' : 'Create New Participant'}
      </button>

      {showCreateForm && (
        <section style={{ marginBottom: '2rem' }}>
          <h2>Create a New Participant</h2>
          <form onSubmit={handleCreateParticipant} style={{ maxWidth: '400px' }}>
            <div style={{ marginBottom: '1rem' }}>
              <label htmlFor="tz">Time Zone</label>
              <br />
              <input
                id="tz"
                type="text"
                value={tz}
                onChange={(e) => setTz(e.target.value)}
                placeholder="e.g., America/Los_Angeles"
                required
              />
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <label htmlFor="studyPid">Study Participant ID</label>
              <br />
              <input
                id="studyPid"
                type="text"
                value={studyPid}
                onChange={(e) => setStudyPid(e.target.value)}
                required
              />
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <label htmlFor="enrolled">Enrolled?</label>
              <br />
              <input
                id="enrolled"
                type="checkbox"
                checked={enrolled}
                onChange={(e) => setEnrolled(e.target.checked)}
              />
            </div>

            <button type="submit">Create Participant</button>
          </form>
        </section>
      )}

      <section>
        <h2>Participants</h2>
        {loading && <p>Loading participants...</p>}
        {error && <p style={{ color: 'red' }}>{error}</p>}

        {!loading && !error && (
          <>
            {participants.length === 0 ? (
              <p>No participants found.</p>
            ) : (
              <table border="1" cellPadding="8" style={{ borderCollapse: 'collapse' }}>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Study PID</th>
                    <th>Time Zone</th>
                    <th>Enrolled</th>
                    <th>Start Date</th>
                  </tr>
                </thead>
                <tbody>
                  {participants.map((participant) => (
                    <tr key={participant.id}>
                      <td>{participant.id}</td>
                      <td>{participant.study_pid}</td>
                      <td>{participant.tz}</td>
                      <td>{participant.enrolled ? 'Yes' : 'No'}</td>
                      <td>{participant.start_date}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </>
        )}

        {/* Pagination controls */}
        <div style={{ marginTop: '1rem' }}>
          <button onClick={handlePreviousPage} disabled={page <= 1}>
            Previous
          </button>
          <span style={{ margin: '0 1rem' }}>
            Page {page} of {totalPages}
          </span>
          <button onClick={handleNextPage} disabled={page >= totalPages}>
            Next
          </button>
        </div>
      </section>
    </div>
  );
}

export default EnrollmentDashboard;