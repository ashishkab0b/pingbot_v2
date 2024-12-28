import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import StudyNav from '../components/StudyNav';
import { useStudy } from '../context/StudyContext';
import axios from '../api/axios';
import DataTable from '../components/DataTable';

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

  // Optional: start_date, telegram_id, etc.
  // e.g. const [telegramId, setTelegramId] = useState('');

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
        // Optional: start_date, telegram_id, etc.
      });
      // Reset form fields
      setTz('');
      setStudyPid('');
      setEnrolled(true);
      // e.g. setTelegramId('');

      setShowCreateForm(false);

      // Refresh the table
      fetchParticipants(studyId, page, perPage);
    } catch (err) {
      console.error(err);
      setError('Error creating participant.');
    }
  };

  // ------------------------------------------------
  // Delete participant
  // ------------------------------------------------
  const handleDeleteParticipant = async (enrollmentId) => {
    if (!window.confirm('Are you sure you want to delete this participant?')) return;

    try {
      await axios.delete(`/studies/${studyId}/enrollments/${enrollmentId}`);
      // Refresh participants list
      fetchParticipants(studyId, page, perPage);
    } catch (err) {
      console.error(err);
      setError('Error deleting participant.');
    }
  };

  // ------------------------------------------------
  // Toggle participant enrollment
  // ------------------------------------------------
  const handleToggleEnrollment = async (enrollmentId, currentStatus) => {
    try {
      // Update the participant's 'enrolled' field to the opposite of currentStatus
      await axios.put(`/studies/${studyId}/enrollments/${enrollmentId}`, {
        enrolled: !currentStatus,
      });
      // Refresh participants list
      fetchParticipants(studyId, page, perPage);
    } catch (err) {
      console.error(err);
      setError('Error updating enrollment status.');
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

      {/* <button
        style={{ marginBottom: '1rem' }}
        onClick={() => setShowCreateForm(!showCreateForm)}
      >
        {showCreateForm ? 'Cancel' : 'Create New Participant'}
      </button> */}

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

            {/*
            <div style={{ marginBottom: '1rem' }}>
              <label htmlFor="telegramId">Telegram ID</label>
              <br />
              <input
                id="telegramId"
                type="text"
                value={telegramId}
                onChange={(e) => setTelegramId(e.target.value)}
              />
            </div>
            */}

            <button type="submit">Create Participant</button>
          </form>
        </section>
      )}

      <section>
        <h2>Participants</h2>
        <DataTable
          data={participants.map((participant) => ({
            ID: participant.id,
            'Study PID': participant.study_pid,
            'Time Zone': participant.tz,
            Enrolled: participant.enrolled ? 'Yes' : 'No',
            'Linked Telegram?': participant.linked_telegram ? 'Yes' : 'No',
            'Start Date': participant.signup_ts_local,
          }))}
          headers={['ID', 'Study PID', 'Time Zone', 'Enrolled', 'Linked Telegram?', 'Start Date']} 
          loading={loading}
          error={error}
          currentPage={page}
          totalPages={totalPages}
          onPreviousPage={handlePreviousPage}
          onNextPage={handleNextPage}
          actionsColumn={(row) => (
            <>
              {/* Enroll/Unenroll button */}
              <button
                onClick={() =>
                  handleToggleEnrollment(row.ID, row.Enrolled === 'Yes')
                }
              >
                {row.Enrolled === 'Yes' ? 'Unenroll' : 'Enroll'}
              </button>

              {/* Delete button */}
              <button
                style={{ marginLeft: '0.5rem' }}
                onClick={() => handleDeleteParticipant(row.ID)}
              >
                Delete
              </button>
            </>
          )}

        />
      </section>
    </div>
  );
}

export default EnrollmentDashboard;