import React from 'react';

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
  return (
    <div>
      {loading && <p>Loading...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}

      {!loading && !error && (
        <>
          {data.length === 0 ? (
            <p>No data found.</p>
          ) : (
            <table border="1" cellPadding="8" style={{ borderCollapse: 'collapse', width: '100%' }}>
              <thead>
                <tr>
                  {headers.map((header, index) => (
                    <th key={index}>{header}</th>
                  ))}
                  {actionsColumn && <th>Actions</th>}
                </tr>
              </thead>
              <tbody>
                {data.map((row, rowIndex) => (
                  <tr
                    key={rowIndex}
                    style={onRowClick ? { cursor: 'pointer' } : {}}
                    onClick={onRowClick ? () => onRowClick(row) : undefined}
                  >
                    {Object.values(row).map((cell, cellIndex) => (
                      <td key={cellIndex}>{cell}</td>
                    ))}
                    {actionsColumn && (
                      <td>
                        {actionsColumn(row)}
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          {/* Pagination Controls */}
          <div style={{ marginTop: '1rem' }}>
            <button onClick={onPreviousPage} disabled={currentPage <= 1}>
              Previous
            </button>
            <span style={{ margin: '0 1rem' }}>
              Page {currentPage} of {totalPages}
            </span>
            <button onClick={onNextPage} disabled={currentPage >= totalPages}>
              Next
            </button>
          </div>
        </>
      )}
    </div>
  );
}

export default DataTable;