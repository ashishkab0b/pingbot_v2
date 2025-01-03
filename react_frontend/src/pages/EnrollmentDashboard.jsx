// EnrollmentDashboard.js

import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import StudyNav from '../components/StudyNav';
import { useStudy } from '../context/StudyContext';
import axios from '../api/axios';
import DataTable from '../components/DataTable';
import { IconButton, Tooltip, Box, Button, TextField, Checkbox, FormControlLabel, Grid } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import PersonRemoveIcon from '@mui/icons-material/PersonRemove';
import Typography from '@mui/material/Typography';

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
  const perPage = 10; // Adjust as needed
  const [totalRows, setTotalRows] = useState(0);

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
      fetchParticipants();
    }
    // eslint-disable-next-line
  }, [studyId, page]);

  const fetchParticipants = async () => {
    setLoading(true);
    setError(null);

    try {
      // GET /studies/<study_id>/enrollments
      const response = await axios.get(`/studies/${studyId}/enrollments`, {
        params: {
          page: page,
          per_page: perPage,
          // Add sorting and searching if needed
        },
      });
      const { data, meta } = response.data;

      setParticipants(data);
      setPage(meta.page);
      setTotalRows(meta.total);
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
        // Optional: telegram_id, etc.
      });
      // Reset form fields
      setTz('');
      setStudyPid('');
      setEnrolled(true);
      // e.g. setTelegramId('');

      setShowCreateForm(false);

      // Refresh the table
      fetchParticipants();
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
      fetchParticipants();
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
      fetchParticipants();
    } catch (err) {
      console.error(err);
      setError('Error updating enrollment status.');
    }
  };

  // ------------------------------------------------
  // Pagination Handler
  // ------------------------------------------------
  const handlePageChange = (newPage) => {
    setPage(newPage);
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
      <Typography variant="h4" gutterBottom>
        Study: {study?.internal_name || 'Loading...'}
      </Typography>
      <StudyNav />

      {/* <Button
        variant="contained"
        color={showCreateForm ? 'secondary' : 'primary'}
        onClick={() => setShowCreateForm(!showCreateForm)}
        sx={{ marginBottom: '1rem' }}
      >
        {showCreateForm ? 'Cancel' : 'Create New Participant'}
      </Button> */}

      {showCreateForm && (
        <Box component="section" sx={{ marginBottom: '2rem' }}>
          <Typography variant="h5" gutterBottom>
            Create a New Participant
          </Typography>
          <Box
            component="form"
            onSubmit={handleCreateParticipant}
            sx={{ maxWidth: 600 }}
            noValidate
            autoComplete="off"
          >
            <Grid container spacing={2}>
              {/* Time Zone */}
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  id="tz"
                  label="Time Zone"
                  value={tz}
                  onChange={(e) => setTz(e.target.value)}
                  required
                  helperText="e.g., America/Los_Angeles"
                />
              </Grid>

              {/* Study Participant ID */}
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  id="studyPid"
                  label="Study Participant ID"
                  value={studyPid}
                  onChange={(e) => setStudyPid(e.target.value)}
                  required
                  helperText="Enter the participant ID assigned in the study."
                />
              </Grid>

              {/* Enrolled Checkbox */}
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={enrolled}
                      onChange={(e) => setEnrolled(e.target.checked)}
                      color="primary"
                    />
                  }
                  label="Enrolled?"
                />
              </Grid>

              {/* Submit Button */}
              <Grid item xs={12}>
                <Button type="submit" variant="contained" color="primary">
                  Create Participant
                </Button>
              </Grid>
            </Grid>
          </Box>
        </Box>
      )}

      <section>
        <DataTable
          data={participants.map((participant) => ({
            id: participant.id,
            studyPid: participant.study_pid,
            timeZone: participant.tz,
            enrolled: participant.enrolled ? 'Yes' : 'No',
            linkedTelegram: participant.linked_telegram ? 'Yes' : 'No',
            startDate: participant.signup_ts,
            prCompleted: participant.pr_completed,
          }))}
          columns={[
            { label: 'ID', key: 'id' },
            { label: 'Participant ID', key: 'studyPid' },
            { label: 'Time Zone', key: 'timeZone' },
            { label: 'Enrolled?', key: 'enrolled' },
            { label: 'Linked Telegram?', key: 'linkedTelegram' },
            { label: 'Enrollment Date', key: 'startDate' },
            { label: 'Proportion completed', key: 'prCompleted' },
          ]}
          loading={loading}
          error={error}
          currentPage={page}
          perPage={perPage}
          totalRows={totalRows}
          onPageChange={handlePageChange}
          actionsColumn={(row) => (
            <Box display="flex">
              {/* Enroll/Unenroll button */}
              <Tooltip title={row.enrolled === 'Yes' ? 'Unenroll Participant' : 'Enroll Participant'}>
                <IconButton
                  color="primary"
                  aria-label={row.enrolled === 'Yes' ? 'Unenroll Participant' : 'Enroll Participant'}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleToggleEnrollment(row.id, row.enrolled === 'Yes');
                  }}
                >
                  {row.enrolled === 'Yes' ? <PersonRemoveIcon /> : <PersonAddIcon />}
                </IconButton>
              </Tooltip>

              {/* Delete button */}
              <Tooltip title="Delete Participant">
                <IconButton
                  color="error"
                  aria-label="Delete Participant"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDeleteParticipant(row.id);
                  }}
                >
                  <DeleteIcon />
                </IconButton>
              </Tooltip>
            </Box>
          )}
        />
      </section>
    </div>
  );
}

export default EnrollmentDashboard;