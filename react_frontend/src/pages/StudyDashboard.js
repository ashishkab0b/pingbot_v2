import React, { useEffect, useState } from 'react';
import axios from '../api/axios';

function StudyDashboard() {
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

  // Form fields for creating a new study
  const [publicName, setPublicName] = useState('');
  const [internalName, setInternalName] = useState('');
  const [contactMessage, setContactMessage] = useState('');

  // Track whether `internalName` was manually edited
  const [internalNameEdited, setInternalNameEdited] = useState(false);

  const handlePublicNameChange = (e) => {
    const value = e.target.value;
    setPublicName(value);

    // Auto-populate `internalName` only if it hasn't been manually edited
    if (!internalNameEdited) {
      setInternalName(value);
    }
  };

  const handleInternalNameChange = (e) => {
    const value = e.target.value;
    setInternalName(value);
    setInternalNameEdited(true); // Mark as manually edited
  };

  // -----------------------------------------
  // NEW: Toggles whether the "Create Study" form is shown
  // -----------------------------------------
  const [showCreateForm, setShowCreateForm] = useState(false);

  // -----------------------------------------
  // Fetch studies on component mount or when page changes
  // -----------------------------------------
  useEffect(() => {
    fetchStudies(page, perPage);
    // eslint-disable-next-line
  }, [page]);

  // -----------------------------------------
  // API call to GET /studies
  // -----------------------------------------
  const fetchStudies = async (currentPage, itemsPerPage) => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.get(
        `/studies?page=${currentPage}&per_page=${itemsPerPage}`
      );

      const { data, meta } = response.data;
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
  // Handle creating a new study (POST /studies)
  // -----------------------------------------
  const handleCreateStudy = async (e) => {
    e.preventDefault();

    try {
      await axios.post('/studies', {
        public_name: publicName,
        internal_name: internalName,
        contact_message: contactMessage,
      });

      // Reset form fields
      setPublicName('');
      setInternalName('');
      setContactMessage('');

      // Optionally hide the form after successful creation
      setShowCreateForm(false);

      // Re-fetch the studies list
      fetchStudies(page, perPage);
    } catch (err) {
      console.error(err);
      setError('Error creating study');
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
  // Render
  // -----------------------------------------
  return (
    <div style={{ margin: '2rem' }}>
      <h1>Studies Dashboard</h1>

      {/* 
        NEW: Button to toggle form visibility 
      */}
      <button
        style={{ marginBottom: '1rem' }}
        onClick={() => setShowCreateForm(!showCreateForm)}
      >
        {showCreateForm ? 'Cancel' : 'Create New Study'}
      </button>

      {/* 
        NEW: Conditionally render the "Create Study" form 
      */}
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
                title="Name of the study as displayed to participants."
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
                title="Name of the study as displayed in researcher interfaces."
                required
              />
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <label htmlFor="contactMessage">Contact Message</label><br />
              <textarea
                id="contactMessage"
                value={contactMessage}
                onChange={(e) => setContactMessage(e.target.value)}
                title="This is a message to participants with instructions on how to contact you, the researcher."
                rows="4"
                style={{ width: '100%' }}
              />
            </div>


            <button type="submit">Create Study</button>
          </form>
        </section>
      )}

      {/* Display Studies in a table */}
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
                    <th>Contact Message</th>
                    <th>Signup Code</th>
                  </tr>
                </thead>
                <tbody>
                  {studies.map((study) => (
                    <tr key={study.id}>
                      <td>{study.id}</td>
                      <td>{study.public_name}</td>
                      <td>{study.internal_name}</td>
                      <td>{study.contact_message}</td>
                      <td>{study.code}</td>
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

export default StudyDashboard;