import React, { useState } from 'react';
import { useParams, useLocation } from 'react-router-dom';
import axios from '../api/axios';

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
  const [tz, setTz] = useState('');
  const [error, setError] = useState(null);
  const [submitted, setSubmitted] = useState(false);
  const [telegramLinkCode, setTelegramLinkCode] = useState(''); // Add state for the code

  const ianaTimezones = [
    'UTC',
    'America/New_York',
    'America/Los_Angeles',
    'America/Chicago',
    'America/Denver',
    'America/Phoenix',
    'Europe/London',
    'Europe/Berlin',
    'Europe/Paris',
    'Asia/Tokyo',
    'Asia/Shanghai',
    'Asia/Singapore',
    'Australia/Sydney',
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
  
    try {
      const response = await axios.post('/signup', {
        signup_code,
        study_pid,
        tz,
      });

      // Assume the server response includes { telegram_link_code: 'some_code' }
      const { telegram_link_code } = response.data;
      setTelegramLinkCode(telegram_link_code); // Store the code in state
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
      <p>
        You are signing up for the study with code: <strong>{signup_code}</strong>  
        <br />
        Participant ID (PID): <strong>{study_pid}</strong>
      </p>

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
          <label htmlFor="tz">
            Select your Timezone:
            <br />
            <select
              id="tz"
              name="tz"
              value={tz}
              onChange={(e) => setTz(e.target.value)}
              required
              style={{ width: '100%', marginTop: '0.5rem' }}
            >
              <option value="">-- Select Timezone --</option>
              {ianaTimezones.map((zone) => (
                <option key={zone} value={zone}>
                  {zone}
                </option>
              ))}
            </select>
          </label>

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