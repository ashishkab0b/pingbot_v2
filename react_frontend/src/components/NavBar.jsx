// Navbar.js
import React from 'react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { logoutUser } from '../api/auth';
import { useDonationDialog } from '../context/DonationDialogContext';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  IconButton,
  Link,
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';

const NavBar = () => {
  const navigate = useNavigate();
  const accessToken = localStorage.getItem('access_token');
  const { openDonationDialog } = useDonationDialog();

  const handleOpenDonation = () => {
    openDonationDialog();
  };
  const handleLogout = async () => {
    if (!accessToken) {
      console.warn('No access token found for logout.');
      navigate('/login');
      return;
    }
    try {
      await logoutUser(accessToken);
    } catch (error) {
      console.error('Logout failed:', error);
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      navigate('/login');
    }
  };

  return (
    <AppBar position="static" color="primary">
      <Toolbar>
        {/* You can add a logo or icon here */}


        {/* Application Title */}
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          EMA Pingbot
        </Typography>

        {/* Navigation Links */}
        {accessToken ? (
          <>
            <Button color="inherit" component={RouterLink} to="/studies">
              Studies
            </Button>
            <Button color="inherit" component={RouterLink} to="/help">
              Help
            </Button>
            <Button color="inherit" onClick={handleOpenDonation}>
              Donate
            </Button>
            {/* <Button color="inherit" component={RouterLink} to="/account">
              Account
            </Button> */}
            <Button color="inherit" onClick={handleLogout}>
              Log Out
            </Button>
          </>
        ) : (
          <>
            <Button color="inherit" component={RouterLink} to="/help">
              Help
            </Button>
            <Button color="inherit" onClick={handleOpenDonation}>
              Donate
            </Button>
            <Button color="inherit" component={RouterLink} to="/login">
              Login
            </Button>

          </>
        )}
      </Toolbar>
    </AppBar>
  );
};

export default NavBar;