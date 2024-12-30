import React, { useState, useMemo, useEffect } from 'react';
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
  TextField,
  Checkbox,
  FormControlLabel,
  Menu,
  MenuItem,
  IconButton,
  Tooltip,
} from '@mui/material';
import { ArrowUpward, ArrowDownward, FilterList } from '@mui/icons-material';

function DataTable({
  data = [],
  columns = [],
  loading = false,
  error = null,
  currentPage = 1,
  totalPages = 1,
  onPreviousPage,
  onNextPage,
  onRowClick = null,
  actionsColumn = null,
}) {
  // State variables for sorting
  const [sortColumn, setSortColumn] = useState(null);
  const [sortDirection, setSortDirection] = useState('asc');
  
  // State variables for search
  const [searchQuery, setSearchQuery] = useState('');
  
  // State variables for column visibility
  const [visibleColumns, setVisibleColumns] = useState(columns);
  
  // State for column visibility menu
  const [anchorEl, setAnchorEl] = useState(null);

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
      if (prevVisibleColumns.find(col => col.key === key)) {
        // Hide the column
        return prevVisibleColumns.filter(col => col.key !== key);
      } else {
        // Show the column
        const newColumn = columns.find(col => col.key === key);
        return [...prevVisibleColumns, newColumn];
      }
    });
  };

  // Handle sorting when a column header is clicked
  const handleSort = (columnKey) => {
    if (sortColumn === columnKey) {
      // Toggle sort direction
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      // Set new sort column and default to ascending
      setSortColumn(columnKey);
      setSortDirection('asc');
    }
  };

  // Update search query state
  const handleSearchInputChange = (event) => {
    setSearchQuery(event.target.value);
  };

  // Reset visible columns when columns prop changes
  useEffect(() => {
    setVisibleColumns(columns);
  }, [columns]);

  // Filter data based on search query
  const filteredData = useMemo(() => {
    if (!searchQuery) return data;

    const lowerCaseQuery = searchQuery.toLowerCase();
    return data.filter((row) =>
      visibleColumns.some((col) => {
        const cellValue = row[col.key];
        return (
          cellValue &&
          cellValue.toString().toLowerCase().includes(lowerCaseQuery)
        );
      })
    );
  }, [data, searchQuery, visibleColumns]);

  // Sort data based on sortColumn and sortDirection
  const sortedData = useMemo(() => {
    if (!sortColumn) return filteredData;

    const sorted = [...filteredData].sort((a, b) => {
      const aValue = a[sortColumn];
      const bValue = b[sortColumn];

      if (aValue == null) return 1;
      if (bValue == null) return -1;

      if (aValue < bValue) {
        return sortDirection === 'asc' ? -1 : 1;
      } else if (aValue > bValue) {
        return sortDirection === 'asc' ? 1 : -1;
      }
      return 0;
    });

    return sorted;
  }, [filteredData, sortColumn, sortDirection]);

  // Pagination setup
  const perPage = 10;
  const totalRows = sortedData.length;
  const totalPageCount = Math.ceil(totalRows / perPage);
  const currentPageData = sortedData.slice(
    (currentPage - 1) * perPage,
    currentPage * perPage
  );

  // Handle page change action
  const handleChangePage = (event, newPage) => {
    if (newPage + 1 > currentPage) {
      onNextPage && onNextPage();
    } else {
      onPreviousPage && onPreviousPage();
    }
  };

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
    return (
      <Typography sx={{ padding: '1rem' }}>No data found.</Typography>
    );
  }

  // Main render
  return (
    <Paper sx={{ width: '100%', padding: '1rem' }}>
      {/* Top Bar with Search and Column Visibility Toggle */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          marginBottom: '1rem',
          flexWrap: 'wrap',
        }}
      >
        {/* Search Input */}
        <TextField
          label="Search"
          variant="outlined"
          size="small"
          value={searchQuery}
          onChange={handleSearchInputChange}
          sx={{ width: '300px', marginBottom: '0.5rem' }}
        />

        {/* Column Visibility Toggle */}
        <div>
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
                      checked={
                        !!visibleColumns.find((vc) => vc.key === col.key)
                      }
                      onChange={() => handleColumnVisibilityChange(col.key)}
                    />
                  }
                  label={col.label}
                />
              </MenuItem>
            ))}
          </Menu>
        </div>
      </div>

      {/* Data Table */}
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              {visibleColumns.map((header) => (
                <TableCell
                  key={header.key}
                  sx={{ fontWeight: 'bold', cursor: 'pointer' }}
                  onClick={() => handleSort(header.key)}
                >
                  {header.label}
                  {sortColumn === header.key &&
                    (sortDirection === 'asc' ? (
                      <ArrowUpward fontSize="small" />
                    ) : (
                      <ArrowDownward fontSize="small" />
                    ))}
                </TableCell>
              ))}
              {actionsColumn && <TableCell>Actions</TableCell>}
            </TableRow>
          </TableHead>
          <TableBody>
            {currentPageData.map((row, rowIndex) => (
              <TableRow
                key={rowIndex}
                hover={!!onRowClick}
                onClick={onRowClick ? () => onRowClick(row) : undefined}
                sx={{ cursor: onRowClick ? 'pointer' : 'default' }}
              >
                {visibleColumns.map((col, cellIndex) => (
                  <TableCell key={cellIndex}>{row[col.key]}</TableCell>
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

export default DataTable;