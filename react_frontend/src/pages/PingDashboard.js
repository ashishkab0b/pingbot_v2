import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import StudyNav from '../components/StudyNav';
import axios from '../api/axios';
import { useStudy } from '../context/StudyContext';
import DataTable from '../components/DataTable';

function PingDashboard() {
  const { studyId } = useParams();
  const study = useStudy();

  // -----------------------------------------
  // State
  // -----------------------------------------
  const [pings, setPings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Pagination
  const [page, setPage] = useState(1);
  const [perPage] = useState(5);
  const [totalPages, setTotalPages] = useState(1);

  // Form fields for creating a new Ping
  // Minimal required fields: enrollment_id, scheduled_ts, day_num
  const [enrollmentId, setEnrollmentId] = useState('');
  const [scheduledTs, setScheduledTs] = useState('');
  const [dayNum, setDayNum] = useState('');
  // Optional fields
  const [pingTemplateId, setPingTemplateId] = useState('');
  // const [message, setMessage] = useState('');
  // const [url, setUrl] = useState('');

  const [showCreateForm, setShowCreateForm] = useState(false);

  // -----------------------------------------
  // API: GET /pings
  // -----------------------------------------
  useEffect(() => {
    if (studyId) {
      fetchPings(studyId, page, perPage);
    }
    // eslint-disable-next-line
  }, [studyId, page]);

  const fetchPings = async (studyId, currentPage, itemsPerPage) => {
    setLoading(true);
    setError(null);

    try {
      // GET /studies/<study_id>/pings?page=...
      const response = await axios.get(
        `/studies/${studyId}/pings?page=${currentPage}&per_page=${itemsPerPage}`
      );
      const { data, meta } = response.data;

      setPings(data);
      setPage(meta.page);
      setTotalPages(meta.pages);
    } catch (err) {
      console.error(err);
      setError('Error fetching pings.');
    } finally {
      setLoading(false);
    }
  };

  // -----------------------------------------
  // API: POST /studies (create ping)
  // -----------------------------------------
  const handleCreatePing = async (e) => {
    e.preventDefault();
    if (!studyId) {
      setError('No studyId found in URL.');
      return;
    }

    try {
      await axios.post(`/studies/${studyId}/pings`, {
        enrollment_id: enrollmentId,
        scheduled_ts: scheduledTs,
        day_num: dayNum,
        ping_template_id: pingTemplateId || null,
        // message: message || null,
        // url: url || null,
      });

      // Reset form
      setEnrollmentId('');
      setScheduledTs('');
      setDayNum('');
      setPingTemplateId('');
      // setMessage('');
      // setUrl('');
      setShowCreateForm(false);

      // Refresh the table
      fetchPings(studyId, page, perPage);
    } catch (err) {
      console.error(err);
      setError('Error creating ping.');
    }
  };
  // -----------------------------------------
  // API: DELETE /studies/:id
  // -----------------------------------------
  const handleDeletePing = async (pingId) => {
    if (!window.confirm('Are you sure you want to delete this ping?')) return;

    try {
      await axios.delete(`/studies/${studyId}/pings/${pingId}`);
      // Refresh studies after deletion
      fetchPings(studyId, page, perPage);
    } catch (err) {
      console.error(err);
      setError('Error deleting study');
    }
  };

  // -----------------------------------------
  // Pagination
  // -----------------------------------------
  const handlePreviousPage = () => {
    if (page > 1) setPage((prev) => prev - 1);
  };

  const handleNextPage = () => {
    if (page < totalPages) setPage((prev) => prev + 1);
  };

  if (!studyId) {
    return <div>Error: Missing studyId in the URL.</div>;
  }

  // -----------------------------------------
  // Render
  // -----------------------------------------
  return (
    <div style={{ margin: '2rem' }}>
      <StudyNav />
      <h1>Pings for {study?.internal_name || 'Loading...'}</h1>

      {/* <button
        style={{ marginBottom: '1rem' }}
        onClick={() => setShowCreateForm(!showCreateForm)}
      >
        {showCreateForm ? 'Cancel' : 'Create New Ping'}
      </button> */}

      {showCreateForm && (
        <section style={{ marginBottom: '2rem' }}>
          <h2>Create a New Ping</h2>
          <form onSubmit={handleCreatePing} style={{ maxWidth: '400px' }}>
            <div style={{ marginBottom: '1rem' }}>
              <label htmlFor="enrollmentId">Participant (Enrollment) ID</label>
              <br />
              <input
                id="enrollmentId"
                type="text"
                value={enrollmentId}
                onChange={(e) => setEnrollmentId(e.target.value)}
                placeholder="1"
                required
              />
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <label htmlFor="scheduledTs">Scheduled Timestamp (UTC)</label>
              <br />
              <input
                id="scheduledTs"
                type="datetime-local"
                value={scheduledTs}
                onChange={(e) => setScheduledTs(e.target.value)}
                required
              />
              {/* Example format might need to be "YYYY-MM-DDTHH:MM" */}
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <label htmlFor="dayNum">Day Number</label>
              <br />
              <input
                id="dayNum"
                type="number"
                value={dayNum}
                onChange={(e) => setDayNum(e.target.value)}
                placeholder="1"
                required
              />
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <label htmlFor="pingTemplateId">Ping Template ID (optional)</label>
              <br />
              <input
                id="pingTemplateId"
                type="text"
                value={pingTemplateId}
                onChange={(e) => setPingTemplateId(e.target.value)}
                placeholder="(if using an existing template)"
              />
            </div>

            <button type="submit">Create Ping</button>
          </form>
        </section>
      )}

<section>
        <h2>Pings</h2>
        <DataTable
          data={pings.map((ping) => ({
            ID: ping.id,
            'Participant ID': ping.pid,
            'Enrollment ID': ping.enrollment_id,
            'Day #': ping.day_num,
            Scheduled: ping.scheduled_ts_local,
            'Ping Sent?': ping.ping_sent ? 'Yes' : 'No',
            'Reminder Sent?': ping.reminder_sent ? 'Yes' : 'No',
          }))}
          headers={[
            'ID',
            'Participant ID',
            'Enrollment ID',
            'Day #',
            'Scheduled',
            'Ping Sent?',
            'Reminder Sent?',
          ]}
          loading={loading}
          error={error}
          currentPage={page}
          totalPages={totalPages}
          onPreviousPage={handlePreviousPage}
          onNextPage={handleNextPage}
          actionsColumn={(row) => (
            <button onClick={() => handleDeletePing(row.ID)}>Delete</button>
          )}
        />
      </section>
    </div>
  );
}

export default PingDashboard;