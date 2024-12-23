
import React, { useState } from 'react';
import { useParams, useLocation } from 'react-router-dom';
import axios from '../api/axios';

function StudyEnroll() {
  // ---------------------------------------------
  // 1. Capture URL params & query params
  // ---------------------------------------------
  const { signup_code } = useParams();
  const location = useLocation();
  // Get the "pid" query parameter: ?pid=<study_pid>
  const searchParams = new URLSearchParams(location.search);
  const study_pid = searchParams.get('pid'); 

  // ---------------------------------------------
  // 2. Local state
  // ---------------------------------------------
  const [tz, setTz] = useState('');
  const [error, setError] = useState(null);
  const [submitted, setSubmitted] = useState(false);

  // ---------------------------------------------
  // 3. Timezone options (you can expand/shorten as you see fit)
  //    For a more complete list, you can import from libraries like
  //    'moment-timezone' or 'react-timezone-select', or define your own array.
  // ---------------------------------------------
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
    // ... add as many as needed
  ];

  // ---------------------------------------------
  // 4. Form submit handler
  // ---------------------------------------------
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
  
    try {
      await axios.post('/signup', {
        signup_code,
        study_pid,
        tz,
      });
  
      setSubmitted(true);
    } catch (err) {
      console.error('Error submitting form:', err);
      setError(
        err.response?.data?.error || 'An error occurred while submitting the form.'
      );
    }
  };

  // ---------------------------------------------
  // 5. Render
  // ---------------------------------------------
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
          <p>Your timezone has been submitted. You can close this page now.</p>
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