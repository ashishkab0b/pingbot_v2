// PingDashboard.js

import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import StudyNav from '../components/StudyNav';
import axios from '../api/axios';
import { useStudy } from '../context/StudyContext';
import DataTable from '../components/DataTable';
import DeleteIcon from '@mui/icons-material/Delete';
import { IconButton, Tooltip, TextField } from '@mui/material';
import { Typography } from '@mui/material';

function PingDashboard() {
  const { studyId } = useParams();
  const study = useStudy();

  // -----------------------------------------
  // State
  // -----------------------------------------
  const [pings, setPings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [totalRows, setTotalRows] = useState(0);

  // Pagination
  const [page, setPage] = useState(1);
  const perPage = 10; // Adjust as needed

  // Sorting and Filtering
  const [sortBy, setSortBy] = useState('id'); // Default sort column
  const [sortOrder, setSortOrder] = useState('asc'); // 'asc' or 'desc'
  const [searchQuery, setSearchQuery] = useState('');

  // -----------------------------------------
  // API: GET /pings
  // -----------------------------------------
  useEffect(() => {
    if (studyId) {
      fetchPings();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [studyId, page, sortBy, sortOrder, searchQuery]);

  const fetchPings = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.get(`/studies/${studyId}/pings`, {
        params: {
          page: page,
          per_page: perPage,
          sort_by: sortBy,
          sort_order: sortOrder,
          search: searchQuery,
        },
      });
      const { data, meta } = response.data;

      setPings(data);
      setTotalRows(meta.total);
      setPage(meta.page);
    } catch (err) {
      console.error(err);
      setError('Error fetching pings.');
    } finally {
      setLoading(false);
    }
  };

  // -----------------------------------------
  // API: DELETE /studies/:study_id/pings/:ping_id
  // -----------------------------------------
  const handleDeletePing = async (pingId) => {
    if (!window.confirm('Are you sure you want to delete this ping?')) return;

    try {
      await axios.delete(`/studies/${studyId}/pings/${pingId}`);
      // Refresh pings after deletion
      fetchPings();
    } catch (err) {
      console.error(err);
      setError('Error deleting ping.');
    }
  };

  // -----------------------------------------
  // Handlers
  // -----------------------------------------
  const handlePageChange = (newPage) => {
    setPage(newPage);
  };

  const handleSortChange = (columnKey) => {
    if (sortBy === columnKey) {
      // Toggle sort order
      setSortOrder((prevOrder) => (prevOrder === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortBy(columnKey);
      setSortOrder('asc');
    }
    setPage(1); // Reset to first page when sort order changes
  };

  const handleSearchChange = (event) => {
    setSearchQuery(event.target.value);
    setPage(1); // Reset to first page when search query changes
  };

  // -----------------------------------------
  // Render
  // -----------------------------------------
  if (!studyId) {
    return <div>Error: Missing studyId in the URL.</div>;
  }

  return (
    <div style={{ margin: '2rem' }}>
      <Typography variant="h4" gutterBottom>
        Study: {study?.internal_name || 'Loading...'}
      </Typography>
      <StudyNav />

      {/* Search Input */}
      <div style={{ marginBottom: '1rem' }}>
        <TextField
          label="Search by Participant ID"
          variant="outlined"
          size="small"
          value={searchQuery}
          onChange={handleSearchChange}
          sx={{ width: '300px' }}
        />
      </div>

      {/* Data Table */}
      <section>
        <DataTable
          data={pings.map((ping) => ({
            id: ping.id,
            participantId: ping.pid,
            // enrollmentId: ping.enrollment_id,
            templateName: ping.ping_template_name,
            dayNum: ping.day_num,
            scheduled: ping.scheduled_ts_local,
            pingSent: ping.sent_ts ? 'Yes' : 'No',
            reminderSent: ping.reminder_sent_ts ? 'Yes' : 'No',
            firstClicked: ping.first_clicked_ts,
          }))}
          columns={[
            { label: 'ID', key: 'id', sortable: true },
            { label: 'Participant ID', key: 'participantId', sortable: true },
            // { label: 'Enrollment ID', key: 'enrollmentId', sortable: true },
            { label: 'Template Name', key: 'templateName', sortable: true },
            { label: 'Day #', key: 'dayNum', sortable: true },
            { label: 'Scheduled', key: 'scheduled', sortable: true },
            { label: 'Ping Sent?', key: 'pingSent', sortable: true },  
            { label: 'Reminder Sent?', key: 'reminderSent', sortable: true },
            { label: 'First Clicked', key: 'firstClicked', sortable: true },
          ]}
          loading={loading}
          error={error}
          currentPage={page}
          perPage={perPage}
          totalRows={totalRows}
          onPageChange={handlePageChange}
          onSortChange={handleSortChange}
          sortBy={sortBy}
          sortOrder={sortOrder}
          actionsColumn={(row) => (
            <Tooltip title="Delete Ping">
              <IconButton
                color="error"
                onClick={(e) => {
                  e.stopPropagation();
                  handleDeletePing(row.id);
                }}
              >
                <DeleteIcon />
              </IconButton>
            </Tooltip>
          )}
        />
      </section>
    </div>
  );
}

export default PingDashboard;