// src/pages/StudyUsers.jsx

import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import StudyNav from '../components/StudyNav';
import axios from '../api/axios';
import DataTable from '../components/DataTable';
import AddUserDialog from '../components/AddUserDialog';
import { useStudy } from '../context/StudyContext';
// import { useAuth } from '../context/AuthContext';
import {
  Typography,
  IconButton,
  Tooltip,
  Select,
  MenuItem,
  FormControl,
  Dialog,
  DialogTitle,
  DialogActions,
  DialogContent,
  Button,
  Alert,
  Box,
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';

function StudyUsers() {
  const { studyId } = useParams();
  // const { currentUser } = useAuth() || {};
  const [email, setEmail] = useState(() => localStorage.getItem('user_email') || '');
  const study = useStudy();

  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // For AddUserDialog
  const [showAddUserDialog, setShowAddUserDialog] = useState(false);

  // Tracks an in-line "role update" approach, or we can do it via a small pop-up.
  // For each user row, we might store a local 'role' in state if we want to allow editing.
  const [updatedRoles, setUpdatedRoles] = useState({});

  // For a possible "confirm remove" dialog
  const [removeDialogOpen, setRemoveDialogOpen] = useState(false);
  const [userToRemove, setUserToRemove] = useState(null);

  useEffect(() => {
    fetchStudyUsers();
    // eslint-disable-next-line
  }, [studyId]);

  const fetchStudyUsers = async () => {
    if (!studyId) return;
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`/studies/${studyId}/users`);
      setUsers(response.data);
    } catch (err) {
      console.error(err);
      setError('Error fetching study users or you do not have permission.');
    } finally {
      setLoading(false);
    }
  };

  // ========== Update user role ========== 
  const handleRoleChange = async (userId, newRole) => {
    // Find the user row in `users`
    const row = users.find((u) => u.user_id === userId);
    if (!row) return;
  
    // Determine what the user’s *current* (old) role is
    // (it might be in updatedRoles if the user previously changed it)
    const oldRole = updatedRoles[userId] || row.role;
  
    // If this row belongs to the logged-in user, and they’re currently owner,
    // and are attempting to switch to anything besides 'owner' → block
    if (row.email === email && oldRole === 'owner' && newRole !== 'owner') {
      setError('You cannot change your own role from owner.');
      return;
    }
  
    // Otherwise proceed with PUT request
    setUpdatedRoles((prev) => ({ ...prev, [userId]: newRole }));
  
    try {
      await axios.put(`/studies/${studyId}/users/${userId}`, { role: newRole });
      fetchStudyUsers();
    } catch (err) {
      console.error(err);
      setError('Error updating user role.');
    }
  };

  // ========== Remove user from study ========== 
  const handleRemoveUser = async () => {
    if (!userToRemove) return;
    try {
      await axios.delete(`/studies/${studyId}/users/${userToRemove}`);
      fetchStudyUsers();
    } catch (err) {
      console.error(err);
      setError('Error removing user.');
    } finally {
      setRemoveDialogOpen(false);
      setUserToRemove(null);
    }
  };

  // Called when user is added from AddUserDialog
  const handleUserAdded = () => {
    setShowAddUserDialog(false);
    fetchStudyUsers();
  };

  // DataTable actions column
  const actionsColumn = (row) => {
    // row has "user_id", "email", "first_name", "last_name", "role"
    return (
      <Tooltip title="Remove from study">
        <IconButton
          color="error"
          onClick={(e) => {
            e.stopPropagation();
            setUserToRemove(row.user_id);
            setRemoveDialogOpen(true);
          }}
        >
          <DeleteIcon />
        </IconButton>
      </Tooltip>
    );
  };

  // DataTable columns
  const columns = [
    {
      label: 'Email',
      key: 'email',
    },
    {
      label: 'Name',
      key: 'name',
      renderCell: (row) => {
        const fullName = `${row.first_name || ''} ${row.last_name || ''}`.trim();
        return fullName || '—'; // fallback if missing
      }
    },
    {
      label: 'Role',
      key: 'role',
      renderCell: (row) => {
        const isMe = row.email === email; // If this row is the currently logged-in user
        return (
          <FormControl size="small">
            <Select
              value={updatedRoles[row.user_id] || row.role}
              onChange={(e) => handleRoleChange(row.user_id, e.target.value)}
              disabled={isMe} // Disable the dropdown if it's your own row
            >
              <MenuItem value="viewer">Viewer</MenuItem>
              <MenuItem value="editor">Editor</MenuItem>
              <MenuItem value="owner">Owner (can share)</MenuItem>
            </Select>
          </FormControl>
        );
      },
    },
  ];

  if (loading) return <p>Loading...</p>;
  if (error) return <Alert severity="error">{error}</Alert>;

  if (!studyId) {
    return <div>Error: Missing studyId in the URL.</div>;
  }

  return (
    <Box sx={{ margin: '2rem' }}>
        <Typography variant="h4" gutterBottom>
        Study: {study?.internal_name || 'Loading...'}
        </Typography>
      <StudyNav />

      <Button
        variant="contained"
        onClick={() => setShowAddUserDialog(true)}
        sx={{ mb: 2 }}
      >
        Add User
      </Button>

      <DataTable
        data={users}
        columns={columns}
        currentPage={1}
        perPage={users.length}
        totalRows={users.length}
        onPageChange={() => {}}
        actionsColumn={actionsColumn}
      />

      {/* AddUserDialog (reused) */}
      <AddUserDialog
        open={showAddUserDialog}
        onClose={() => setShowAddUserDialog(false)}
        studyId={studyId}
        onUserAdded={handleUserAdded}
      />

      {/* Confirm Remove Dialog */}
      <Dialog
        open={removeDialogOpen}
        onClose={() => setRemoveDialogOpen(false)}
      >
        <DialogTitle>Remove User from Study</DialogTitle>
        <DialogContent>
          Are you sure you want to remove this user from the study?
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRemoveDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleRemoveUser} color="error" variant="contained">
            Remove
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default StudyUsers;