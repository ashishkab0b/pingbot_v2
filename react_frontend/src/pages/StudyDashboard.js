import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import DataTable from '../components/DataTable';
import axios from '../api/axios';
import DeleteIcon from '@mui/icons-material/Delete';
import { IconButton, Tooltip } from '@mui/material';

function StudyDashboard() {
  const navigate = useNavigate();

  const userEmail = localStorage.getItem('user_email');

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
    // API: DELETE /studies/:id
    // -----------------------------------------
    const handleDeleteStudy = async (studyId) => {
      if (!window.confirm('Are you sure you want to delete this study?')) return;

      try {
        await axios.delete(`/studies/${studyId}`);
        // Refresh studies after deletion
        fetchStudies(page, perPage);
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
              <span className="form-description">
                This label will be used to identify the study to participants.
              </span><br />
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
              <span className="form-description">
                This label will be used to identify the study internally.
              </span><br />
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
              <span className="form-description">
                This is a message that can be accessed by participants in order to find information on how they should contact you.<br />
              </span><br />
              <textarea
                id="contactMessage"
                placeholder={`For questions or concerns about the study, please email the researchers at ${userEmail || '...'}`}
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
        <DataTable
          data={studies.map((study) => ({
            id: study.id,
            publicName: study.public_name,
            internalName: study.internal_name,
            signupCode: study.code,
            contactMessage: study.contact_message,
          }))}
          columns={[
            { label: 'ID', key: 'id' },
            { label: 'Public Name', key: 'publicName' },
            { label: 'Internal Name', key: 'internalName' },
            { label: 'Signup Code', key: 'signupCode' },
            { label: 'Contact Message', key: 'contactMessage' },
          ]}
          loading={loading}
          error={error}
          currentPage={page}
          totalPages={totalPages}
          onPreviousPage={handlePreviousPage}
          onNextPage={handleNextPage}
          actionsColumn={(row) => (
            <Tooltip title="Delete Study">
              <IconButton
                color="error"
                onClick={(e) => {
                  e.stopPropagation();
                  handleDeleteStudy(row.id);
                }}
              >
                <DeleteIcon />
              </IconButton>
            </Tooltip>
          )}
          onRowClick={(row) => navigate(`/studies/${row.id}`)}
        />
      </section>
    </div>
  );
}

export default StudyDashboard;