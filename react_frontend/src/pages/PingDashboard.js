import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import StudyNav from '../components/StudyNav';
import axios from '../api/axios';
import { useStudy } from '../context/StudyContext';

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
  const [message, setMessage] = useState('');
  const [url, setUrl] = useState('');

  const [showCreateForm, setShowCreateForm] = useState(false);

  // -----------------------------------------
  // Fetch pings whenever page or studyId changes
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
  // Create a new ping
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
        message: message || null,
        url: url || null,
      });

      // Reset form
      setEnrollmentId('');
      setScheduledTs('');
      setDayNum('');
      setPingTemplateId('');
      setMessage('');
      setUrl('');
      setShowCreateForm(false);

      // Refresh the table
      fetchPings(studyId, page, perPage);
    } catch (err) {
      console.error(err);
      setError('Error creating ping.');
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

      <button
        style={{ marginBottom: '1rem' }}
        onClick={() => setShowCreateForm(!showCreateForm)}
      >
        {showCreateForm ? 'Cancel' : 'Create New Ping'}
      </button>

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

            <div style={{ marginBottom: '1rem' }}>
              <label htmlFor="message">Message (optional)</label>
              <br />
              <textarea
                id="message"
                rows={3}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
              />
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <label htmlFor="url">URL (optional)</label>
              <br />
              <input
                id="url"
                type="text"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
              />
            </div>

            <button type="submit">Create Ping</button>
          </form>
        </section>
      )}

      <section>
        <h2>Existing Pings</h2>
        {loading && <p>Loading pings...</p>}
        {error && <p style={{ color: 'red' }}>{error}</p>}

        {!loading && !error && (
          <>
            {pings.length === 0 ? (
              <p>No pings found.</p>
            ) : (
              <table border="1" cellPadding="8" style={{ borderCollapse: 'collapse' }}>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Enrollment ID</th>
                    <th>Day #</th>
                    <th>Scheduled</th>
                    <th>Ping Sent?</th>
                    <th>Reminder Sent?</th>
                    <th>Message</th>
                  </tr>
                </thead>
                <tbody>
                  {pings.map((ping) => (
                    <tr key={ping.id}>
                      <td>{ping.id}</td>
                      <td>{ping.enrollment_id}</td>
                      <td>{ping.day_num}</td>
                      <td>{ping.scheduled_ts}</td>
                      <td>{ping.ping_sent ? 'Yes' : 'No'}</td>
                      <td>{ping.reminder_sent ? 'Yes' : 'No'}</td>
                      <td>{ping.message}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </>
        )}

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

export default PingDashboard;