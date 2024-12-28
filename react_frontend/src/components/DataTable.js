import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  CircularProgress,
  Typography,
  TablePagination
} from '@mui/material';

function DataTable({
  data = [],
  headers = [],
  loading = false,
  error = null,
  currentPage = 1,
  totalPages = 1,
  onPreviousPage,
  onNextPage,
  onRowClick = null,
  actionsColumn = null,
}) {
  // Calculate total number of rows for pagination
  const totalRows = totalPages * data.length;
  const rowsPerPage = data.length;

  const handleChangePage = (event, newPage) => {
    if (newPage + 1 > currentPage) {
      onNextPage();
    } else {
      onPreviousPage();
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: '1rem' }}>
        <CircularProgress />
      </div>
    );
  }

  if (error) {
    return (
      <Typography color="error" sx={{ padding: '1rem' }}>
        {error}
      </Typography>
    );
  }

  if (!data.length) {
    return (
      <Typography sx={{ padding: '1rem' }}>
        No data found.
      </Typography>
    );
  }

  return (
    <Paper sx={{ width: '100%' }}>
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              {headers.map((header, index) => (
                <TableCell key={index} sx={{ fontWeight: 'bold' }}>
                  {header}
                </TableCell>
              ))}
              {actionsColumn && <TableCell>Actions</TableCell>}
            </TableRow>
          </TableHead>
          <TableBody>
            {data.map((row, rowIndex) => (
              <TableRow
                key={rowIndex}
                hover={!!onRowClick}
                onClick={onRowClick ? () => onRowClick(row) : undefined}
                sx={{ cursor: onRowClick ? 'pointer' : 'default' }}
              >
                {Object.values(row).map((cell, cellIndex) => (
                  <TableCell key={cellIndex}>{cell}</TableCell>
                ))}
                {actionsColumn && (
                  <TableCell>
                    {actionsColumn(row)}
                  </TableCell>
                )}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      <TablePagination
        component="div"
        count={totalRows}
        page={currentPage - 1}
        onPageChange={handleChangePage}
        rowsPerPage={rowsPerPage}
        rowsPerPageOptions={[rowsPerPage]}
      />
    </Paper>
  );
}

export default DataTable;