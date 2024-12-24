
import React from 'react';
import { Link } from 'react-router-dom';
// import './NavBar.css'; // Optional for styling

const NavBar = () => {
  return (
    <nav className="navbar">
      <ul className="navbar-list">
        <li className="navbar-item">
          <Link to="/studies">Studies</Link>
        </li>
        <li className="navbar-item">
          <Link to="/account">Account</Link>
        </li>
        <li className="navbar-item">
          <Link to="/logout">Logout (NON FUNCTIONING)</Link>
        </li>
      </ul>
    </nav>
  );
};

export default NavBar;