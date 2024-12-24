import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from '../api/axios';

function StudyDashboard() {
  const navigate = useNavigate();

  // -----------------------------------------
  // State
  // -----------------------------------------
  const [studies, setStudies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Pagination
  const [page, setPage] = useState(1);
  const [perPage] = useState(5);
  const [totalPages, setTotalPages] = useState(1);

  // -----------------------------------------
  // Fields for creating a new study
  // -----------------------------------------
  const [publicName, setPublicName] = useState('');
  const [internalName, setInternalName] = useState('');
  const [contactMessage, setContactMessage] = useState('');

  // Track whether `internalName` was manually edited
  const [internalNameEdited, setInternalNameEdited] = useState(false);

  const handlePublicNameChange = (e) => {
    const value = e.target.value;
    setPublicName(value);

    if (!internalNameEdited) {
      setInternalName(value);
    }
  };

  const handleInternalNameChange = (e) => {
    const value = e.target.value;
    setInternalName(value);
    setInternalNameEdited(true);
  };

  // Toggle whether the "Create Study" form is shown
  const [showCreateForm, setShowCreateForm] = useState(false);

  // -----------------------------------------
  // Fetch studies on mount or when page changes
  // -----------------------------------------
  useEffect(() => {
    fetchStudies(page, perPage);
    // eslint-disable-next-line
  }, [page]);

  // -----------------------------------------
  // API: GET /studies
  // -----------------------------------------
  const fetchStudies = async (currentPage, itemsPerPage) => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.get(`/studies?page=${currentPage}&per_page=${itemsPerPage}`);
      const { data, meta } = res.data;
      setStudies(data);
      setPage(meta.page);
      setTotalPages(meta.pages);
    } catch (err) {
      console.error(err);
      setError('Error fetching studies');
    } finally {
      setLoading(false);
    }
  };

  // -----------------------------------------
  // API: POST /studies (create study)
  // -----------------------------------------
  const handleCreateStudy = async (e) => {
    e.preventDefault();
    try {
      await axios.post('/studies', {
        public_name: publicName,
        internal_name: internalName,
        contact_message: contactMessage,
      });
      // Clear form
      setPublicName('');
      setInternalName('');
      setContactMessage('');
      setInternalNameEdited(false);

      // Hide form
      setShowCreateForm(false);

      // Refresh the studies list
      fetchStudies(page, perPage);
    } catch (err) {
      console.error(err);
      setError('Error creating study');
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

  // -----------------------------------------
  // Render
  // -----------------------------------------
  return (
    <div style={{ margin: '2rem' }}>
      <h1>Studies Dashboard</h1>

      <button
        style={{ marginBottom: '1rem' }}
        onClick={() => setShowCreateForm(!showCreateForm)}
      >
        {showCreateForm ? 'Cancel' : 'Create New Study'}
      </button>

      {/* Conditionally render the "Create Study" form */}
      {showCreateForm && (
        <section style={{ marginBottom: '2rem' }}>
          <h2>Create a New Study</h2>
          <form onSubmit={handleCreateStudy} style={{ maxWidth: '400px' }}>
            <div style={{ marginBottom: '1rem' }}>
              <label htmlFor="publicName">Public Name</label><br />
              <input
                id="publicName"
                type="text"
                value={publicName}
                onChange={handlePublicNameChange}
                required
              />
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <label htmlFor="internalName">Internal Name</label><br />
              <input
                id="internalName"
                type="text"
                value={internalName}
                onChange={handleInternalNameChange}
                required
              />
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <label htmlFor="contactMessage">Contact Message</label><br />
              <textarea
                id="contactMessage"
                rows="4"
                value={contactMessage}
                onChange={(e) => setContactMessage(e.target.value)}
              />
            </div>

            <button type="submit">Create Study</button>
          </form>
        </section>
      )}

      {/* Display the studies in a simplified table */}
      <section>
        <h2>Your Studies</h2>
        {loading && <p>Loading studies...</p>}
        {error && <p style={{ color: 'red' }}>{error}</p>}

        {!loading && !error && (
          <>
            {studies.length === 0 ? (
              <p>No studies found.</p>
            ) : (
              <table border="1" cellPadding="8" style={{ borderCollapse: 'collapse' }}>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Public Name</th>
                    <th>Internal Name</th>
                    <th>Signup Code</th>
                  </tr>
                </thead>
                <tbody>
                  {studies.map((study) => (
                    <tr
                      key={study.id}
                      style={{ cursor: 'pointer' }}
                      onClick={() => navigate(`/studies/${study.id}`)}
                      title="Click to view study details"
                    >
                      <td>{study.id}</td>
                      <td>{study.public_name}</td>
                      <td>{study.internal_name}</td>
                      <td>{study.code}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </>
        )}

        {/* Pagination Controls */}
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

export default StudyDashboard;