// ViewStudy.jsx

import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import StudyNav from '../components/StudyNav';
import axios from '../api/axios';
import {
  Typography,
  Box,
  Paper,
  Grid,
  LinearProgress,
  Alert,
  TextField,
  IconButton,
  Tooltip,
  InputAdornment,
  Button,
} from '@mui/material';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';

// Make sure this component file exists in your project.
// import AddUserDialog from '../components/AddUserDialog';

function ViewStudy() {
  const { studyId } = useParams();

  const [study, setStudy] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // For the "Add User" dialog
  // const [showAddUserDialog, setShowAddUserDialog] = useState(false);

  // For copying enrollment link
  const [participantId, setParticipantId] = useState('');
  const [copied, setCopied] = useState(false);

  // Fetch the study details
  useEffect(() => {
    fetchStudyDetail(studyId);
    // eslint-disable-next-line
  }, [studyId]);

  const fetchStudyDetail = async (id) => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`/studies/${id}`);
      setStudy(response.data);
    } catch (err) {
      console.error(err);
      setError('Error fetching study details');
    } finally {
      setLoading(false);
    }
  };

  // Base URL for enrollment
  const enrollmentLinkBase =
    import.meta.env.VITE_BASE_URL + '/enroll/' + study?.code + '?pid=';

  // Handle link copying
  const handleCopyLink = () => {
    const linkToCopy = `${enrollmentLinkBase}${participantId}`;

    if (navigator.clipboard?.writeText) {
      navigator.clipboard.writeText(linkToCopy).then(
        () => {
          setCopied(true);
          setTimeout(() => setCopied(false), 2000);
        },
        (err) => {
          console.error('Copy failed', err);
          fallbackCopyTextToClipboard(linkToCopy);
        }
      );
    } else {
      fallbackCopyTextToClipboard(linkToCopy);
    }
  };

  // Fallback if `navigator.clipboard` not available
  const fallbackCopyTextToClipboard = (text) => {
    const textArea = document.createElement('textarea');
    textArea.value = text;

    // Avoid scrolling to bottom
    textArea.style.position = 'fixed';
    textArea.style.top = 0;
    textArea.style.left = 0;
    textArea.style.width = '2em';
    textArea.style.height = '2em';
    textArea.style.padding = 0;
    textArea.style.border = 'none';
    textArea.style.outline = 'none';
    textArea.style.boxShadow = 'none';
    textArea.style.background = 'transparent';

    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();

    try {
      const successful = document.execCommand('copy');
      if (successful) {
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      } else {
        alert('Failed to copy the link');
      }
    } catch (err) {
      console.error('Fallback: Could not copy text', err);
      alert('Failed to copy the link');
    }

    document.body.removeChild(textArea);
  };

  // Handler when a user is added in the AddUserDialog
  const handleUserAdded = () => {
    // For now, you can simply log or refresh study details if needed:
    console.log('User was added to the study!');
    // If you have a user list to display, call a function here to re-fetch that data.
  };

  if (loading)
    return (
      <Box sx={{ padding: '2rem' }}>
        <LinearProgress />
      </Box>
    );

  if (error)
    return (
      <Box sx={{ padding: '2rem' }}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );

  if (!study)
    return (
      <Box sx={{ padding: '2rem' }}>
        <Alert severity="warning">
          Study not found or you do not have access.
        </Alert>
      </Box>
    );

  return (
    <Box sx={{ margin: '2rem' }}>
      <Typography variant="h4" gutterBottom>
        Study: {study.internal_name}
      </Typography>

      {/* Navigation Tabs (Overview, Enrollments, etc.) */}
      <StudyNav studyId={studyId} />

      {/* Display study details */}
      <Paper sx={{ padding: '2rem', marginBottom: '2rem' }}>
        <Typography variant="h5" gutterBottom>
          Overview
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle1">
              <strong>Public Name:</strong>
            </Typography>
            <Typography variant="body1">{study.public_name}</Typography>
          </Grid>

          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle1">
              <strong>Internal Name:</strong>
            </Typography>
            <Typography variant="body1">{study.internal_name}</Typography>
          </Grid>

          <Grid item xs={12}>
            <Typography variant="subtitle1">
              <strong>Contact Message:</strong>
            </Typography>
            <Typography variant="body1">{study.contact_message}</Typography>
          </Grid>

          <Grid item xs={12}>
            <Typography variant="subtitle1">
              <strong>Enrollment Link:</strong>
            </Typography>
            <Box sx={{ marginTop: '0.5rem' }}>
              <Grid container spacing={2} alignItems="center">
                <Grid item xs={12} sm={4}>
                  <TextField
                    label="Participant ID"
                    placeholder="Enter Participant ID"
                    variant="outlined"
                    value={participantId}
                    onChange={(e) => setParticipantId(e.target.value)}
                    fullWidth
                  />
                </Grid>
                <Grid item xs={12} sm={8}>
                  <TextField
                    label="Enrollment Link"
                    variant="outlined"
                    value={`${enrollmentLinkBase}${participantId}`}
                    InputProps={{
                      readOnly: true,
                      endAdornment: (
                        <InputAdornment position="end">
                          <Tooltip
                            title={copied ? 'Copied!' : 'Copy to Clipboard'}
                            arrow
                          >
                            <IconButton onClick={handleCopyLink} edge="end">
                              <ContentCopyIcon />
                            </IconButton>
                          </Tooltip>
                        </InputAdornment>
                      ),
                    }}
                    fullWidth
                  />
                </Grid>
              </Grid>
              <Typography
                variant="caption"
                color="textSecondary"
                sx={{ display: 'block', marginTop: '0.5rem' }}
              >
                Send this link to participants to enroll them in the study.
                Remember to replace the <em>Participant ID</em> with the actual
                participant's ID.
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* =================== Add User to Study Section =================== */}
      {/* <Paper sx={{ padding: '2rem', marginBottom: '2rem' }}>
        <Typography variant="h5" gutterBottom>
          Add Users to Study
        </Typography>
        <Button
          variant="contained"
          onClick={() => setShowAddUserDialog(true)}
          sx={{ marginTop: '1rem' }}
        >
          Add User
        </Button>
      </Paper> */}

      {/* The AddUserDialog. It only appears if showAddUserDialog = true */}
      {/* <AddUserDialog
        open={showAddUserDialog}
        onClose={() => setShowAddUserDialog(false)}
        studyId={studyId}
        onUserAdded={handleUserAdded} // callback after success
      /> */}
    </Box>
  );
}

export default ViewStudy;