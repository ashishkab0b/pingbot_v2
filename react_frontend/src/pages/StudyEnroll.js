// StudyEnroll.js

import React, { useState } from 'react';
import { useParams, useLocation } from 'react-router-dom';
import axios from '../api/axios';

// Import Material-UI components
import {
  Typography,
  Box,
  Button,
  Alert,
  CircularProgress,
} from '@mui/material';

// Import the timezone select component
import TimezoneSelect from 'react-timezone-select';

// Import styles for TimezoneSelect (optional, if needed)
// import 'react-timezone-select/dist/react-timezone-select.css';

function StudyEnroll() {
  // ---------------------------------------------
  // 1. Capture URL params & query params
  // ---------------------------------------------
  const { signup_code } = useParams();
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const study_pid = searchParams.get('pid');

  // ---------------------------------------------
  // 2. Local state
  // ---------------------------------------------
  const [tz, setTz] = useState(Intl.DateTimeFormat().resolvedOptions().timeZone);
  const [error, setError] = useState(null);
  const [submitted, setSubmitted] = useState(false);
  const [telegramLinkCode, setTelegramLinkCode] = useState('');
  const [loading, setLoading] = useState(false);

  // ---------------------------------------------
  // Early exit if pid is missing
  // ---------------------------------------------
  if (!study_pid) {
    return (
      <Box sx={{ margin: '2rem' }}>
        <Typography variant="h4" gutterBottom>
          Error
        </Typography>
        <Typography variant="body1">
          Missing participant ID. Please contact the researcher for assistance.
        </Typography>
      </Box>
    );
  }

  // ---------------------------------------------
  // 3. Form submission
  // ---------------------------------------------
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const response = await axios.post('/signup', {
        signup_code,
        study_pid,
        tz,
      });

      const { telegram_link_code } = response.data;
      setTelegramLinkCode(telegram_link_code);
      setSubmitted(true);
    } catch (err) {
      console.error('Error submitting form:', err);
      setError(
        err.response?.data?.error || 'An error occurred while submitting the form.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ margin: '2rem' }}>
      {!submitted ? (
        <>
          <Typography variant="h4" gutterBottom>
            Study Enrollment
          </Typography>
          <Typography variant="body1" gutterBottom>
            Please select your timezone to enroll in the study.
          </Typography>

          <Box
            component="form"
            onSubmit={handleSubmit}
            sx={{ maxWidth: 400, marginTop: '1rem' }}
            noValidate
          >
            <Typography variant="subtitle1" gutterBottom>
              Select your Timezone:
            </Typography>

            {/* Style TimezoneSelect to match MUI components */}
            <Box sx={{ marginBottom: '1rem' }}>
              <TimezoneSelect
                value={tz}
                onChange={(newVal) => setTz(newVal.value ?? newVal)}
                styles={{
                  control: (provided) => ({
                    ...provided,
                    borderColor: 'rgba(0, 0, 0, 0.23)',
                    '&:hover': {
                      borderColor: 'rgba(0, 0, 0, 0.87)',
                    },
                    boxShadow: 'none',
                  }),
                }}
              />
            </Box>

            {error && (
              <Alert severity="error" sx={{ marginBottom: '1rem' }}>
                {error}
              </Alert>
            )}

            <Button
              type="submit"
              variant="contained"
              color="primary"
              disabled={loading}
              fullWidth
            >
              {loading ? <CircularProgress size={24} /> : 'Submit'}
            </Button>
          </Box>
        </>
      ) : (
        <Box sx={{ marginTop: '2rem' }}>
          <Typography variant="h5" gutterBottom>
            Thank you!
          </Typography>
          <Typography variant="body1" paragraph>
            Please download the Telegram app on your phone from your phone's app store.
          </Typography>
          <Typography variant="body1" paragraph>
            After downloading the app, open a conversation with the user{' '}
            <strong>@SurveyPingBot</strong>. You will be asked to provide a code.
          </Typography>
          <Typography variant="body1">
            Enter your code:{' '}
            <strong>{telegramLinkCode || 'ERROR: NO CODE FOUND'}</strong>
          </Typography>
        </Box>
      )}
    </Box>
  );
}

export default StudyEnroll;