import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { logoutUser } from '../api/auth';
// import './NavBar.css'; // Optional for styling

const NavBar = () => {
  const navigate = useNavigate();
  const accessToken = localStorage.getItem('access_token');

  const handleLogout = async () => {
    if (!accessToken) {
      console.warn('No access token found for logout.');
      navigate('/login');
      return;
    }

    try {
      await logoutUser(accessToken); // Ensure the logout API uses the correct key
    } catch (error) {
      console.error('Logout failed:', error);
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      navigate('/login');
    }
  };

  return (
    <nav className="navbar">
      <ul className="navbar-list">
        {accessToken ? (
          <>
            <li className="navbar-item">
              <Link to="/studies">Studies</Link>
            </li>
            <li className="navbar-item">
              <Link to="/account">Account</Link>
            </li>
            <li className="navbar-item">
              <a href="/logout" onClick={(e) => { e.preventDefault(); handleLogout(); }}>
                Log Out
              </a>
            </li>
          </>
        ) : (
          <li className="navbar-item">
            <Link to="/login">Login</Link>
          </li>
        )}
      </ul>
    </nav>
  );
};

export default NavBar;