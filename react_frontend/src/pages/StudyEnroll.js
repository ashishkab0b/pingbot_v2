import React, { useState } from 'react';
import { useParams, useLocation } from 'react-router-dom';
import axios from '../api/axios';

// 1) Import the timezone select component
import TimezoneSelect from 'react-timezone-select';

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

  // ---------------------------------------------
  // Early exit if pid is missing
  // ---------------------------------------------
  if (!study_pid) {
    return (
      <div style={{ margin: '2rem' }}>
        <h1>Error</h1>
        <p>Missing participant ID. Please contact the researcher for assistance.</p>
      </div>
    );
  }

  // ---------------------------------------------
  // 3. Form submission
  // ---------------------------------------------
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
  
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
    }
  };

  return (
    <div style={{ margin: '2rem' }}>
      <h1>Study Enroll</h1>

      {submitted ? (
        <div style={{ marginTop: '2rem' }}>
          <h2>Thank you!</h2>
          <p>Please download the Telegram app on your phone from your phone's app store.</p>
          <p>
            After downloading the app, open a conversation with the user @SurveyPingBot. 
            You will be asked to provide a code. Enter <strong>{telegramLinkCode || 'ERROR: NO CODE FOUND'}</strong>.
          </p>
        </div>
      ) : (
        <form onSubmit={handleSubmit} style={{ maxWidth: '400px', marginTop: '1rem' }}>
          <label htmlFor="tz">Select your Timezone:</label>
          <br />
          <TimezoneSelect
            id="tz"
            value={tz}
            onChange={(newVal) => setTz(newVal.value ?? newVal)}
            style={{ width: '100%', marginTop: '0.5rem' }}
          />

          {error && (
            <p style={{ color: 'red', marginTop: '1rem' }}>
              {error}
            </p>
          )}

          <button type="submit" style={{ marginTop: '1rem' }}>
            Submit
          </button>
        </form>
      )}
    </div>
  );
}

export default StudyEnroll;