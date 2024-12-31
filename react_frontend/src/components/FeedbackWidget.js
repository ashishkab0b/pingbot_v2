// FeedbackWidget.js

import React, { useState } from 'react';
import {
  Fab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Checkbox,
  FormControlLabel,
  Button,
  Select,
  MenuItem,
  InputLabel,
  FormControl,
  CircularProgress,
  Tooltip,
} from '@mui/material';
import FeedbackIcon from '@mui/icons-material/Feedback';
import axios from '../api/axios'; // Adjust the import path as needed

function FeedbackWidget() {
  const [open, setOpen] = useState(false);
  const [feedbackType, setFeedbackType] = useState('General feedback');
  const [message, setMessage] = useState('');
  const [isUrgent, setIsUrgent] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [email, setEmail] = useState('');

  const feedbackTypes = [
    'Feature request',
    'Bug report',
    'Support request',
    'General feedback',
  ];

  const handleOpen = () => setOpen(true);
  const handleClose = () => {
    if (!submitting) {
      setOpen(false);
      // Reset the form
      setFeedbackType('General feedback');
      setMessage('');
      setIsUrgent(false);
      setEmail('');
      setSubmitted(false);
    }
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      // Adjust the request payload to match your Flask route expectations
      await axios.post('/support', {
        email: email,
        type: feedbackType, // The Flask route expects 'type' as 'query_type'
        message: message,
        urgent: isUrgent,
      });
      setSubmitted(true);
    } catch (error) {
      console.error('Error submitting feedback:', error);
      alert(
        'There was an error submitting your feedback. Please try again later.'
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <>
      <Tooltip title="Send Feedback">
        <Fab
          color="primary"
          onClick={handleOpen}
          sx={{
            position: 'fixed',
            bottom: (theme) => theme.spacing(2),
            right: (theme) => theme.spacing(2),
          }}
        >
          <FeedbackIcon />
        </Fab>
      </Tooltip>

      <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle>Submit Feedback</DialogTitle>
        {submitting && (
          <DialogContent sx={{ textAlign: 'center' }}>
            <CircularProgress />
            <p>Submitting your feedback...</p>
          </DialogContent>
        )}
        {!submitting && !submitted && (
          <>
            {/* Add padding to the top of DialogContent */}
            <DialogContent sx={{ paddingTop: 2 }}>
              {/* Use margin="normal" for consistent spacing */}
              <FormControl fullWidth margin="normal">
                <InputLabel id="feedback-type-label">Feedback Type</InputLabel>
                <Select
                  labelId="feedback-type-label"
                  id="feedback-type-select"
                  value={feedbackType}
                  label="Feedback Type"
                  onChange={(e) => setFeedbackType(e.target.value)}
                >
                  {feedbackTypes.map((type) => (
                    <MenuItem key={type} value={type}>
                      {type}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <TextField
                label="Your Email"
                type="email"
                fullWidth
                variant="outlined"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                margin="normal"
              />

              <TextField
                label="Your Feedback"
                multiline
                rows={4}
                fullWidth
                variant="outlined"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                required
                margin="normal"
              />

              <FormControlLabel
                control={
                  <Checkbox
                    checked={isUrgent}
                    onChange={(e) => setIsUrgent(e.target.checked)}
                  />
                }
                label="Mark as urgent"
                sx={{ marginTop: 1 }}
              />
            </DialogContent>
            <DialogActions>
              <Button onClick={handleClose} disabled={submitting}>
                Cancel
              </Button>
              <Button
                onClick={handleSubmit}
                variant="contained"
                color="primary"
                disabled={!message.trim() || !email.trim() || submitting}
              >
                Submit
              </Button>
            </DialogActions>
          </>
        )}
        {!submitting && submitted && (
          <>
            <DialogContent>
              <p>Thank you for your feedback!</p>
            </DialogContent>
            <DialogActions>
              <Button onClick={handleClose}>Close</Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </>
  );
}

export default FeedbackWidget;