// ViewStudy.js

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
} from '@mui/material';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';

function ViewStudy() {
  const { studyId } = useParams();

  const [study, setStudy] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

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

  const enrollmentLinkBase = `${process.env.REACT_APP_BASE_URL}/enroll/${study?.code}?pid=`;

  const handleCopyLink = () => {
    const linkToCopy = `${enrollmentLinkBase}${participantId}`;
    navigator.clipboard.writeText(linkToCopy).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
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
                Remember to replace the <em>Participant ID</em> with the actual participant's ID.
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
}

export default ViewStudy;