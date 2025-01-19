import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import axios from '../api/axios';

function AddUserDialog({ open, onClose, studyId, onUserAdded }) {
  const [email, setEmail] = useState('');
  const [role, setRole] = useState('viewer');
  const [error, setError] = useState(null);

  const handleSubmit = async () => {
    setError(null);
    try {
      const response = await axios.post(`/studies/${studyId}/add_user`, {
        email,
        role
      });
      // If successful, we can either show a success message or refresh data
      if (onUserAdded) {
        onUserAdded();
      }
      // Clear input
      setEmail('');
      setRole('viewer');
      onClose();
    } catch (err) {
      // If error, set message
      const msg = err?.response?.data?.error || 'Error adding user';
      setError(msg);
    }
  };

  const handleClose = () => {
    // Optional: reset state on close
    setEmail('');
    setRole('viewer');
    setError(null);
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="xs" fullWidth>
      <DialogTitle>Add User to Study</DialogTitle>
      <DialogContent dividers>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        <TextField
          required
          fullWidth
          label="User Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          type="email"
          margin="dense"
        />
        <FormControl fullWidth margin="dense">
          <InputLabel>Role</InputLabel>
          <Select
            label="Role"
            value={role}
            onChange={(e) => setRole(e.target.value)}
          >
            <MenuItem value="viewer">Viewer</MenuItem>
            <MenuItem value="editor">Editor</MenuItem>
            <MenuItem value="owner">Owner (can share)</MenuItem>
          </Select>
        </FormControl>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} color="secondary">Cancel</Button>
        <Button onClick={handleSubmit} variant="contained">
          Add
        </Button>
      </DialogActions>
    </Dialog>
  );
}

export default AddUserDialog;