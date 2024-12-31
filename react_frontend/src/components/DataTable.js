// DataTable.js

import React from 'react';
import PropTypes from 'prop-types';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress,
  Typography,
  TablePagination,
  IconButton,
  Tooltip,
  Menu,
  MenuItem,
  FormControlLabel,
  Checkbox,
} from '@mui/material';
import { ArrowUpward, ArrowDownward, FilterList } from '@mui/icons-material';

function DataTable({
  data = [],
  columns = [],
  loading = false,
  error = null,
  currentPage = 1,
  perPage = 10,
  totalRows = 0,
  onPageChange,
  onSortChange,
  sortBy,
  sortOrder,
  onRowClick = null,
  actionsColumn = null,
}) {
  // State variables for column visibility
  const [visibleColumns, setVisibleColumns] = React.useState(columns);

  // State for column visibility menu
  const [anchorEl, setAnchorEl] = React.useState(null);

  // Handle opening of column visibility menu
  const handleToggleColumnsMenu = (event) => {
    setAnchorEl(event.currentTarget);
  };

  // Handle closing of column visibility menu
  const handleCloseColumnsMenu = () => {
    setAnchorEl(null);
  };

  // Handle changes in column visibility
  const handleColumnVisibilityChange = (key) => {
    setVisibleColumns((prevVisibleColumns) => {
      if (prevVisibleColumns.find((col) => col.key === key)) {
        // Hide the column
        return prevVisibleColumns.filter((col) => col.key !== key);
      } else {
        // Show the column
        const newColumn = columns.find((col) => col.key === key);
        // Insert the column back to its original position
        const updatedColumns = [...prevVisibleColumns];
        const insertIndex = columns.findIndex((col) => col.key === key);
        updatedColumns.splice(insertIndex, 0, newColumn);
        return updatedColumns;
      }
    });
  };

  // Handle sorting when a column header is clicked
  const handleSort = (columnKey, sortable) => {
    if (!sortable) return;
    if (onSortChange) {
      onSortChange(columnKey);
    }
  };

  // Handle page change action
  const handleChangePage = (event, newPage) => {
    if (onPageChange) {
      onPageChange(newPage + 1); // Material-UI uses zero-based page index
    }
  };

  // Reset visible columns when columns prop changes
  React.useEffect(() => {
    setVisibleColumns(columns);
  }, [columns]);

  // Render loading state
  if (loading) {
    return (
      <div
        style={{ display: 'flex', justifyContent: 'center', padding: '1rem' }}
      >
        <CircularProgress />
      </div>
    );
  }

  // Render error state
  if (error) {
    return (
      <Typography color="error" sx={{ padding: '1rem' }}>
        {error}
      </Typography>
    );
  }

  // Render empty data state
  if (!data.length) {
    return <Typography sx={{ padding: '1rem' }}>No data found.</Typography>;
  }

  // Main render
  return (
    <Paper sx={{ width: '100%', padding: '1rem' }}>
      {/* Column Visibility Toggle */}
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '1rem' }}>
        <Tooltip title="Show/Hide Columns">
          <IconButton onClick={handleToggleColumnsMenu}>
            <FilterList />
          </IconButton>
        </Tooltip>
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleCloseColumnsMenu}
        >
          {columns.map((col) => (
            <MenuItem key={col.key}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={!!visibleColumns.find((vc) => vc.key === col.key)}
                    onChange={() => handleColumnVisibilityChange(col.key)}
                  />
                }
                label={col.label}
              />
            </MenuItem>
          ))}
        </Menu>
      </div>

      {/* Data Table */}
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              {visibleColumns.map((header) => (
                <TableCell
                  key={header.key}
                  sx={{ fontWeight: 'bold', cursor: header.sortable ? 'pointer' : 'default' }}
                  onClick={() => handleSort(header.key, header.sortable)}
                >
                  {header.label}
                  {header.sortable && sortBy === header.key && (
                    sortOrder === 'asc' ? (
                      <ArrowUpward fontSize="small" />
                    ) : (
                      <ArrowDownward fontSize="small" />
                    )
                  )}
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
                {visibleColumns.map((col, cellIndex) => (
                  <TableCell key={cellIndex}>
                    {col.renderCell ? col.renderCell(row) : row[col.key]}
                  </TableCell>
                ))}
                {actionsColumn && (
                  <TableCell>{actionsColumn(row)}</TableCell>
                )}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Pagination Controls */}
      <TablePagination
        component="div"
        count={totalRows}
        page={currentPage - 1}
        onPageChange={handleChangePage}
        rowsPerPage={perPage}
        rowsPerPageOptions={[perPage]}
      />
    </Paper>
  );
}

DataTable.propTypes = {
  data: PropTypes.array.isRequired,
  columns: PropTypes.array.isRequired,
  loading: PropTypes.bool,
  error: PropTypes.string,
  currentPage: PropTypes.number.isRequired,
  perPage: PropTypes.number,
  totalRows: PropTypes.number.isRequired,
  onPageChange: PropTypes.func.isRequired,
  onSortChange: PropTypes.func,
  sortBy: PropTypes.string,
  sortOrder: PropTypes.oneOf(['asc', 'desc']),
  onRowClick: PropTypes.func,
  actionsColumn: PropTypes.func,
};

export default DataTable;