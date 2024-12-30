// src/pages/ParticipantFacingDashboard.js

import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import axios from 'axios';

// Material-UI components
import {
  Container,
  Typography,
  CircularProgress,
  TableContainer,
  Paper,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  Alert,
} from '@mui/material';

function useQuery() {
  return new URLSearchParams(useLocation().search);
}

function ParticipantFacingDashboard() {
  const query = useQuery();

  const [enrollments, setEnrollments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Get the 't' and 'otp' query parameters from the URL
  const telegramId = query.get('t');
  const otp = query.get('otp');

  useEffect(() => {
    async function fetchEnrollments() {
      try {
        const response = await axios.get(`${process.env.REACT_APP_API_URL}/participant_dashboard`, {
          params: {
            t: telegramId,
            otp: otp,
          },
        });
        setEnrollments(response.data);
        setLoading(false);
      } catch (err) {
        console.error(err);
        setError(
          err.response && err.response.data && err.response.data.error
            ? err.response.data.error
            : 'An unknown error occurred'
        );
        setLoading(false);
      }
    }
    fetchEnrollments();
  }, [telegramId, otp]);

  if (loading) {
    return (
      <Container sx={{ marginTop: 4 }}>
        <CircularProgress />
      </Container>
    );
  }

  if (error) {
    return (
      <Container sx={{ marginTop: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  if (enrollments.length === 0) {
    return (
      <Container sx={{ marginTop: 4 }}>
        <Typography variant="h6">You are not enrolled in any studies.</Typography>
      </Container>
    );
  }

  return (
    <Container sx={{ marginTop: 4 }}>
      <Typography variant="h4" gutterBottom>
        Your Studies
      </Typography>
      <TableContainer component={Paper}>
        <Table sx={{ minWidth: 650 }} aria-label="Enrollments Table">
          <TableHead>
            <TableRow>
              <TableCell>Study Name</TableCell>
              <TableCell>Participant ID</TableCell>
              <TableCell>Time Zone</TableCell>
              <TableCell>Enrolled?</TableCell>
              <TableCell>Signup Date</TableCell>
              <TableCell>Contact Message</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {enrollments.map((enrollment, index) => (
              <TableRow key={index}>
                <TableCell>{enrollment.public_name}</TableCell>
                <TableCell>{enrollment.study_pid}</TableCell>
                <TableCell>{enrollment.tz}</TableCell>
                <TableCell>{enrollment.enrolled ? 'Yes' : 'No'}</TableCell>
                <TableCell>{enrollment.signup_ts}</TableCell>
                <TableCell>{enrollment.contact_message}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Container>
  );
}

export default ParticipantFacingDashboard;