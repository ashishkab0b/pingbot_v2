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
  Link,
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

  // Construct a deep link to Telegram. The "?start=" parameter can be replaced with
  // any code you want the bot to receive automatically.
  const telegramDeepLink = `https://t.me/SurveyPingBot?start=${encodeURIComponent('/start')}`;

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
          {/* <Typography variant="h5" gutterBottom>
            Thank You for Enrolling!
          </Typography> */}

          {/* Step 1: Download Telegram Instructions */}
          <Typography variant="body1" paragraph>
            To receive study notifications, you’ll need the Telegram app <em>on your phone</em>. (Please be sure to use your phone, not a computer, so you can receive notifications while away from your computer.) 
            Below are links to download Telegram for both iOS (iPhone/iPad) and Android:
          </Typography>

          <Box sx={{ mb: 2 }}>
            <Typography variant="body1">
              • <Link href="https://apps.apple.com/app/telegram-messenger/id686449807" target="_blank" rel="noopener">
                  Download Telegram for iOS
                </Link>
            </Typography>
            <Typography variant="body1">
              • <Link href="https://play.google.com/store/apps/details?id=org.telegram.messenger" target="_blank" rel="noopener">
                  Download Telegram for Android
                </Link>
            </Typography>
          </Box>

          {/* Step 2: Open Bot Conversation */}
          <Typography variant="body1" paragraph>
            After you’ve installed Telegram, please open a conversation with our study bot, <strong>@SurveyPingBot</strong>.
            To do this automatically, you can click the link below. It will open Telegram and pre-fill a <code>/start</code> command:
          </Typography>

          <Box sx={{ mb: 2 }}>
            <Link
              href={telegramDeepLink}
              target="_blank"
              rel="noopener"
              underline="always"
              sx={{ wordWrap: 'break-word' }}
            >
              {telegramDeepLink}
            </Link>
          </Box>

          {/* Step 3: Provide the Enrollment Code */}
          <Typography variant="body1" paragraph>
            Once inside the conversation with <strong>@SurveyPingBot</strong>, enter <code>/enroll</code>. You will then be asked to provide an enrollment code. 
            Please provide the following code exactly as shown below:
          </Typography>

          <Typography variant="h1" sx={{ mt: 2 }}>
            {telegramLinkCode || 'ERROR: NO CODE FOUND'}
          </Typography>

          <Typography variant="body1" paragraph>
            If you have any questions or need assistance, please contact the researcher.
          </Typography>

        </Box>
      )}
    </Box>
  );
}

export default StudyEnroll;