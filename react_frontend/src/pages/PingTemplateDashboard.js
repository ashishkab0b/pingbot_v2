import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import StudyNav from '../components/StudyNav';
import { useStudy } from '../context/StudyContext';
import axios from '../api/axios'; 

function PingTemplateDashboard() {
  // -----------------------------------------
  // Get studyId from the URL parameter
  // -----------------------------------------
  const { studyId } = useParams();
  const study = useStudy();

  // -----------------------------------------
  // State
  // -----------------------------------------
  const [pingTemplates, setPingTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Pagination
  const [page, setPage] = useState(1);
  const [perPage] = useState(5);
  const [totalPages, setTotalPages] = useState(1);

  // Form fields for creating a new Ping Template
  const [name, setName] = useState('');
  const [message, setMessage] = useState('');
  const [url, setUrl] = useState('');
  const [reminderLatency, setReminderLatency] = useState('');
  const [expireLatency, setExpireLatency] = useState('');
  const [schedule, setSchedule] = useState('');

  // Toggle for "Create Ping Template" form
  const [showCreateForm, setShowCreateForm] = useState(false);
  

  // -----------------------------------------
  // Fetch ping templates whenever page or studyId changes
  // -----------------------------------------
  useEffect(() => {
    if (studyId) {
      fetchPingTemplates(studyId, page, perPage);
    }
    // eslint-disable-next-line
  }, [page, studyId]);

  // -----------------------------------------
  // API call to GET ping templates
  // -----------------------------------------
  const fetchPingTemplates = async (studyId, currentPage, itemsPerPage) => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.get(
        `/studies/${studyId}/ping_templates?page=${currentPage}&per_page=${itemsPerPage}`
      );
      const { data, meta } = response.data;

      setPingTemplates(data);
      setPage(meta.page);
      setTotalPages(meta.pages);
    } catch (err) {
      console.error(err);
      setError('Error fetching ping templates');
    } finally {
      setLoading(false);
    }
  };

  // -----------------------------------------
  // Handle creating a new ping template
  // -----------------------------------------
  const handleCreatePingTemplate = async (e) => {
    e.preventDefault();

    try {
      // If the user typed JSON for schedule, parse it
      const scheduleParsed = schedule ? JSON.parse(schedule) : null;

      await axios.post(`/studies/${studyId}/ping_templates`, {
        name,
        message,
        url,
        reminder_latency: reminderLatency,
        expire_latency: expireLatency,
        schedule: scheduleParsed,
      });

      // Reset form fields
      setName('');
      setMessage('');
      setUrl('');
      setReminderLatency('');
      setExpireLatency('');
      setSchedule('');

      // Hide the form
      setShowCreateForm(false);

      // Re-fetch ping templates
      fetchPingTemplates(studyId, page, perPage);
    } catch (err) {
      console.error(err);
      setError('Error creating ping template');
    }
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
  // Render fallback if studyId is missing
  // -----------------------------------------
  if (!studyId) {
    return <div>Error: Missing studyId in the URL.</div>;
  }

  // -----------------------------------------
  // Render
  // -----------------------------------------
  return (
    <div style={{ margin: '2rem' }}>
      <StudyNav />
      <h1>Ping Templates for {study?.internal_name || 'Loading...'}</h1>

      <button
        style={{ marginBottom: '1rem' }}
        onClick={() => setShowCreateForm(!showCreateForm)}
      >
        {showCreateForm ? 'Cancel' : 'Create New Ping Template'}
      </button>

      {showCreateForm && (
        <section style={{ marginBottom: '2rem' }}>
          <h2>Create a New Ping Template</h2>
          <form onSubmit={handleCreatePingTemplate} style={{ maxWidth: '400px' }}>
            <div style={{ marginBottom: '1rem' }}>
              <label htmlFor="name">Name</label>
              <br />
              <input
                id="name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <label htmlFor="message">Message</label>
              <br />
              <textarea
                id="message"
                rows={4}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                required
              />
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <label htmlFor="url">URL</label>
              <br />
              <input
                id="url"
                type="text"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
              />
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <label htmlFor="reminder">
                Reminder Latency (e.g. 1 hour, 30 minutes)
              </label>
              <br />
              <input
                id="reminder"
                type="text"
                value={reminderLatency}
                onChange={(e) => setReminderLatency(e.target.value)}
              />
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <label htmlFor="expire">Expire Latency (e.g. 24 hours)</label>
              <br />
              <input
                id="expire"
                type="text"
                value={expireLatency}
                onChange={(e) => setExpireLatency(e.target.value)}
              />
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <label htmlFor="schedule">Schedule (JSON)</label>
              <br />
              <textarea
                id="schedule"
                rows={4}
                value={schedule}
                onChange={(e) => setSchedule(e.target.value)}
                placeholder='e.g. [{"day":1,"time":"09:00:00"}]'
              />
            </div>

            <button type="submit">Create Ping Template</button>
          </form>
        </section>
      )}

      <section>
        <h2>Your Ping Templates</h2>
        {loading && <p>Loading ping templates...</p>}
        {error && <p style={{ color: 'red' }}>{error}</p>}

        {!loading && !error && (
          <>
            {pingTemplates.length === 0 ? (
              <p>No ping templates found.</p>
            ) : (
              <table
                border="1"
                cellPadding="8"
                style={{ borderCollapse: 'collapse' }}
              >
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Message</th>
                    <th>URL</th>
                    <th>Reminder Latency</th>
                    <th>Expire Latency</th>
                    <th>Schedule</th>
                  </tr>
                </thead>
                <tbody>
                  {pingTemplates.map((pt) => (
                    <tr key={pt.id}>
                      <td>{pt.id}</td>
                      <td>{pt.name}</td>
                      <td>{pt.message}</td>
                      <td>{pt.url}</td>
                      <td>{pt.reminder_latency}</td>
                      <td>{pt.expire_latency}</td>
                      <td>{JSON.stringify(pt.schedule)}</td>
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

export default PingTemplateDashboard;