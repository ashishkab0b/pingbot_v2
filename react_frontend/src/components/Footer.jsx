// Footer.js
import React from 'react';
import { Box, Typography } from '@mui/material';

const Footer = () => (
  <Box
    sx={{
      backgroundColor: 'grey.200', // Subtle background color
      color: 'grey.600', // Subtle text color
      padding: 1, // Reduced padding
      position: 'fixed',
      bottom: 0,
      width: '100%',
      borderTop: '1px solid grey.300', // Optional subtle border
    }}
  >
    <Typography variant="body2" align="center">
      &copy; {new Date().getFullYear()} Ashish Mehta
    </Typography>
  </Box>
);

export default Footer;