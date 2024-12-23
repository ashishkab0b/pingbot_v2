import React, { useEffect, useState } from 'react';
import axios from '../api/axios';

function PingDashboard() {
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

  // Advanced Search Fields
  const [searchStudyId, setSearchStudyId] = useState('');
  const [searchDayNum, setSearchDayNum] = useState('');
  const [searchMessage, setSearchMessage] = useState('');
  const [searchEnrollmentId, setSearchEnrollmentId] = useState('');

  // Create/Update form fields
  const [editMode, setEditMode] = useState(false); // false = create, true = update
  const [selectedPingId, setSelectedPingId] = useState(null);

  const [studyId, setStudyId] = useState('');
  const [pingTemplateId, setPingTemplateId] = useState('');
  const [enrollmentId, setEnrollmentId] = useState('');
  const [scheduledTs, setScheduledTs] = useState('');
  const [expireTs, setExpireTs] = useState('');
  const [reminderTs, setReminderTs] = useState('');
  const [dayNum, setDayNum] = useState('');
  const [message, setMessage] = useState('');
  const [url, setUrl] = useState('');

  // -----------------------------------------
  // Fetch pings on component mount or when page changes or advanced search changes
  // -----------------------------------------
  useEffect(() => {
    fetchPings();
    // eslint-disable-next-line
  }, [page]);

  // -----------------------------------------
  // API call to GET /pings with optional query params
  // -----------------------------------------
  const fetchPings = async () => {
    setLoading(true);
    setError(null);

    try {
      // Build the query string for advanced search
      const queryParams = new URLSearchParams();
      queryParams.append('page', page);
      queryParams.append('per_page', perPage);

      if (searchStudyId) queryParams.append('study_id', searchStudyId);
      if (searchDayNum) queryParams.append('day_num', searchDayNum);
      if (searchMessage) queryParams.append('message', searchMessage);
      if (searchEnrollmentId) queryParams.append('enrollment_id', searchEnrollmentId);

      const response = await axios.get(`/pings?${queryParams.toString()}`);
      const { data, meta } = response.data;
      setPings(data);
      setPage(meta.page);
      setTotalPages(meta.pages);
    } catch (err) {
      console.error(err);
      setError('Error fetching pings');
    } finally {
      setLoading(false);
    }
  };

  // -----------------------------------------
  // Handle "Search" button click
  // -----------------------------------------
  const handleSearch = (e) => {
    e.preventDefault();
    setPage(1); // Reset to first page after searching
    fetchPings();
  };

  // -----------------------------------------
  // Handle create or update submission
  // -----------------------------------------
  const handleSubmit = async (e) => {
    e.preventDefault();

    // Gather form data
    const pingData = {
      study_id: studyId,
      ping_template_id: pingTemplateId,
      enrollment_id: enrollmentId,
      scheduled_ts: scheduledTs,
      expire_ts: expireTs,
      reminder_ts: reminderTs,
      day_num: dayNum,
      message: message,
      url: url
    };

    try {
      if (!editMode) {
        // CREATE
        await axios.post('/pings', pingData);
      } else {
        // UPDATE
        await axios.put(`/pings/${selectedPingId}`, pingData);
      }

      // Reset the form
      resetForm();
      // Refresh the list
      fetchPings();
    } catch (err) {
      console.error(err);
      setError('Error creating/updating ping');
    }
  };

  // -----------------------------------------
  // Handle click on "Edit" button
  // -----------------------------------------
  const handleEditClick = (ping) => {
    setEditMode(true);
    setSelectedPingId(ping.id);

    // Populate form fields
    setStudyId(ping.study_id);
    setPingTemplateId(ping.ping_template_id || '');
    setEnrollmentId(ping.enrollment_id);
    setScheduledTs(ping.scheduled_ts || '');
    setExpireTs(ping.expire_ts || '');
    setReminderTs(ping.reminder_ts || '');
    setDayNum(ping.day_num);
    setMessage(ping.message || '');
    setUrl(ping.url || '');
  };

  // -----------------------------------------
  // Handle "Delete" button click
  // -----------------------------------------
  const handleDelete = async (pingId) => {
    if (!window.confirm('Are you sure you want to delete this ping?')) return;

    try {
      await axios.delete(`/pings/${pingId}`);
      fetchPings();
    } catch (err) {
      console.error(err);
      setError('Error deleting ping');
    }
  };

  // -----------------------------------------
  // Reset form fields
  // -----------------------------------------
  const resetForm = () => {
    setEditMode(false);
    setSelectedPingId(null);
    setStudyId('');
    setPingTemplateId('');
    setEnrollmentId('');
    setScheduledTs('');
    setExpireTs('');
    setReminderTs('');
    setDayNum('');
    setMessage('');
    setUrl('');
  };

  // -----------------------------------------
  // Simple pagination handlers
  // -----------------------------------------
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

  // -----------------------------------------
  // Render
  // -----------------------------------------
  return (
    <div style={{ margin: '2rem' }}>
      <h1>Pings Dashboard</h1>

      {/* Advanced Search Section */}
      <section style={{ marginBottom: '2rem' }}>
        <h2>Advanced Search</h2>
        <form onSubmit={handleSearch} style={{ display: 'flex', gap: '1rem' }}>
          <div>
            <label>Study ID: </label>
            <input
              type="number"
              value={searchStudyId}
              onChange={(e) => setSearchStudyId(e.target.value)}
              placeholder="Study ID"
            />
          </div>
          <div>
            <label>Day Num: </label>
            <input
              type="number"
              value={searchDayNum}
              onChange={(e) => setSearchDayNum(e.target.value)}
              placeholder="Day Num"
            />
          </div>
          <div>
            <label>Message Contains: </label>
            <input
              type="text"
              value={searchMessage}
              onChange={(e) => setSearchMessage(e.target.value)}
              placeholder="Message..."
            />
          </div>
          <div>
            <label>Enrollment ID: </label>
            <input
              type="number"
              value={searchEnrollmentId}
              onChange={(e) => setSearchEnrollmentId(e.target.value)}
              placeholder="Enrollment ID"
            />
          </div>
          <button type="submit">Search</button>
          <button type="button" onClick={() => {
            // Reset search fields
            setSearchStudyId('');
            setSearchDayNum('');
            setSearchMessage('');
            setSearchEnrollmentId('');
            setPage(1);
            fetchPings();
          }}>
            Clear
          </button>
        </form>
      </section>

      {/* Create/Update Ping Section */}
      <section style={{ marginBottom: '2rem' }}>
        <h2>{editMode ? 'Update' : 'Create'} Ping</h2>
        <form onSubmit={handleSubmit} style={{ maxWidth: '600px' }}>
          <div style={{ marginBottom: '0.5rem' }}>
            <label htmlFor="studyId">Study ID</label><br />
            <input
              id="studyId"
              type="number"
              value={studyId}
              onChange={(e) => setStudyId(e.target.value)}
              required
            />
          </div>

          <div style={{ marginBottom: '0.5rem' }}>
            <label htmlFor="pingTemplateId">Ping Template ID (optional)</label><br />
            <input
              id="pingTemplateId"
              type="number"
              value={pingTemplateId}
              onChange={(e) => setPingTemplateId(e.target.value)}
            />
          </div>

          <div style={{ marginBottom: '0.5rem' }}>
            <label htmlFor="enrollmentId">Enrollment ID</label><br />
            <input
              id="enrollmentId"
              type="number"
              value={enrollmentId}
              onChange={(e) => setEnrollmentId(e.target.value)}
              required
            />
          </div>

          <div style={{ marginBottom: '0.5rem' }}>
            <label htmlFor="scheduledTs">Scheduled Timestamp</label><br />
            <input
              id="scheduledTs"
              type="datetime-local"
              value={scheduledTs}
              onChange={(e) => setScheduledTs(e.target.value)}
              required
            />
          </div>

          <div style={{ marginBottom: '0.5rem' }}>
            <label htmlFor="expireTs">Expire Timestamp (optional)</label><br />
            <input
              id="expireTs"
              type="datetime-local"
              value={expireTs}
              onChange={(e) => setExpireTs(e.target.value)}
            />
          </div>

          <div style={{ marginBottom: '0.5rem' }}>
            <label htmlFor="reminderTs">Reminder Timestamp (optional)</label><br />
            <input
              id="reminderTs"
              type="datetime-local"
              value={reminderTs}
              onChange={(e) => setReminderTs(e.target.value)}
            />
          </div>

          <div style={{ marginBottom: '0.5rem' }}>
            <label htmlFor="dayNum">Day Num</label><br />
            <input
              id="dayNum"
              type="number"
              value={dayNum}
              onChange={(e) => setDayNum(e.target.value)}
              required
            />
          </div>

          <div style={{ marginBottom: '0.5rem' }}>
            <label htmlFor="message">Message (optional)</label><br />
            <textarea
              id="message"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              rows={3}
            />
          </div>

          <div style={{ marginBottom: '0.5rem' }}>
            <label htmlFor="url">URL (optional)</label><br />
            <input
              id="url"
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
            />
          </div>

          <button type="submit">{editMode ? 'Update' : 'Create'} Ping</button>
          {editMode && (
            <button type="button" onClick={resetForm} style={{ marginLeft: '1rem' }}>
              Cancel
            </button>
          )}
        </form>
      </section>

      {/* Display Pings in a table */}
      <section>
        <h2>Your Pings</h2>
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
                    <th>Study ID</th>
                    <th>Enrollment ID</th>
                    <th>Day Num</th>
                    <th>Scheduled</th>
                    <th>Message</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {pings.map((ping) => (
                    <tr key={ping.id}>
                      <td>{ping.id}</td>
                      <td>{ping.study_id}</td>
                      <td>{ping.enrollment_id}</td>
                      <td>{ping.day_num}</td>
                      <td>{ping.scheduled_ts}</td>
                      <td>{ping.message}</td>
                      <td>
                        <button onClick={() => handleEditClick(ping)}>Edit</button>
                        <button style={{ marginLeft: '0.5rem' }} onClick={() => handleDelete(ping.id)}>
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </>
        )}

        {/* Simple Pagination Controls */}
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