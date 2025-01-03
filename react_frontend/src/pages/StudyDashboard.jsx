import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import DataTable from '../components/DataTable';
import axios from '../api/axios';
import DeleteIcon from '@mui/icons-material/Delete';
import DonationDialog from '../components/DonationDialog';
import {
  IconButton,
  Tooltip,
  Button,
  TextField,
  Typography,
  Box,
  Grid,
} from '@mui/material';



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
  const [totalRows, setTotalRows] = useState(0);

  // Fields for creating a new study
  const [publicName, setPublicName] = useState('');
  const [internalName, setInternalName] = useState('');
  const [contactMessage, setContactMessage] = useState('');
  const [errors, setErrors] = useState({}); // For validation errors

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


  // Track whether donation dialog is open
  const [showDonationDialog, setShowDonationDialog] = useState(false);

  // Fetch studies on mount or when page changes
  useEffect(() => {
    fetchStudies(page, perPage);
    // eslint-disable-next-line
  }, [page]);

  // API: GET /studies
  const fetchStudies = async (currentPage, itemsPerPage) => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.get(`/studies`, {
        params: {
          page: currentPage,
          per_page: itemsPerPage,
        },
      });
      const { data, meta } = res.data;
      setStudies(data);
      setPage(meta.page);
      // Update totalRows with the total number of studies
      setTotalRows(meta.total);
    } catch (err) {
      console.error(err);
      setError('Error fetching studies');
    } finally {
      setLoading(false);
    }
  };

  // API: POST /studies (create study)
  const handleCreateStudy = async (e) => {
    e.preventDefault();
    setErrors({}); // Reset errors
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

      // SHOW the donation dialog
      setShowDonationDialog(true);

    } catch (err) {
      if (err.response && err.response.status === 400) {
        setErrors(err.response.data.errors || {});
      } else {
        console.error(err);
        setError('Error creating study');
      }
    }
  };

  // API: DELETE /studies/:id
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

  // Pagination
  const handlePageChange = (newPage) => {
    setPage(newPage);
  };

  // Render
  return (
    <div style={{ margin: '2rem' }}>
      <Typography variant="h4" gutterBottom>
        Studies Dashboard
      </Typography>

      <Button
        variant="contained"
        color={showCreateForm ? 'secondary' : 'primary'}
        onClick={() => setShowCreateForm(!showCreateForm)}
        sx={{ marginBottom: '1rem' }}
      >
        {showCreateForm ? 'Cancel' : 'Create New Study'}
      </Button>

      {/* Conditionally render the "Create Study" form */}
      {showCreateForm && (
        <Box component="section" sx={{ marginBottom: '2rem' }}>
          <Typography variant="h5" gutterBottom>
            Create a New Study
          </Typography>
          <Box
            component="form"
            onSubmit={handleCreateStudy}
            sx={{ maxWidth: 600 }}
            noValidate
            autoComplete="off"
          >
            <Grid container spacing={2}>
              {/* Public Name */}
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  id="publicName"
                  label="Public Name"
                  value={publicName}
                  onChange={handlePublicNameChange}
                  required
                  helperText={
                    errors.public_name ||
                    'This label will be used to identify the study to participants.'
                  }
                  error={Boolean(errors.public_name)}
                />
              </Grid>

              {/* Internal Name */}
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  id="internalName"
                  label="Internal Name"
                  value={internalName}
                  onChange={handleInternalNameChange}
                  required
                  helperText={
                    errors.internal_name ||
                    'This label will be used to identify the study internally.'
                  }
                  error={Boolean(errors.internal_name)}
                />
              </Grid>

              {/* Contact Message */}
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  id="contactMessage"
                  label="Contact Message"
                  value={contactMessage}
                  onChange={(e) => setContactMessage(e.target.value)}
                  placeholder={`For questions or concerns about the study, please email the researchers at ${userEmail || '...'}`}
                  multiline
                  rows={4}
                  helperText={
                    errors.contact_message ||
                    'This message provides participants information on how to contact you.'
                  }
                  error={Boolean(errors.contact_message)}
                />
              </Grid>

              {/* Submit Button */}
              <Grid item xs={12}>
                <Button type="submit" variant="contained" color="primary">
                  Create Study
                </Button>
              </Grid>
            </Grid>
          </Box>
        </Box>
      )}

      {/* Display the studies in a simplified table */}
      {/* <section>
        <DataTable
          data={studies.map((study) => ({
            id: study.id,
            publicName: study.public_name,
            internalName: study.internal_name,
            contactMessage: study.contact_message,
          }))}
          columns={[
            { label: 'ID', key: 'id' },
            { label: 'Public Name', key: 'publicName' },
            { label: 'Internal Name', key: 'internalName' },
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
      </section> */}
      <section>
        <DataTable
          data={studies.map((study) => ({
            id: study.id,
            publicName: study.public_name,
            internalName: study.internal_name,
            contactMessage: study.contact_message,
          }))}
          columns={[
            { label: 'ID', key: 'id' },
            { label: 'Public Name', key: 'publicName' },
            { label: 'Internal Name', key: 'internalName' },
            { label: 'Contact Message', key: 'contactMessage' },
          ]}
          loading={loading}
          error={error}
          currentPage={page}
          perPage={perPage}
          totalRows={totalRows}
          onPageChange={handlePageChange}
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

      {/* Donation Prompt Dialog */}
      <DonationDialog
        open={showDonationDialog}
        onClose={() => setShowDonationDialog(false)}
      />
    </div>
  );
}

export default StudyDashboard;