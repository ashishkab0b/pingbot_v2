import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { registerUser } from '../api/auth';

function Register() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [firstname, setFirstname] = useState('');
  const [lastname, setLastname] = useState('');
  const [institution, setInstitution] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await registerUser({ 
        email, 
        password, 
        firstname, 
        lastname, 
        institution 
      });
      alert('Registered successfully!');
      navigate('/login');
    } catch (error) {
      console.error(error);
      alert('Registration failed. Check console for details.');
    }
  };

  return (
    <div style={{ margin: '2rem' }}>
      <h1>Register</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Email:</label><br />
          <input 
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)} 
            required
          />
        </div>
        <div>
          <label>Password:</label><br />
          <input 
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)} 
            required
          />
        </div>
        <div>
          <label>First Name:</label><br />
          <input 
            type="text"
            value={firstname}
            onChange={(e) => setFirstname(e.target.value)} 
            required
          />
        </div>
        <div>
          <label>Last Name:</label><br />
          <input 
            type="text"
            value={lastname}
            onChange={(e) => setLastname(e.target.value)} 
            required
          />
        </div>
        <div>
          <label>Institution:</label><br />
          <input 
            type="text"
            value={institution}
            onChange={(e) => setInstitution(e.target.value)} 
            required
          />
        </div>
        <button style={{ marginTop: '1rem' }} type="submit">
          Register
        </button>
      </form>
    </div>
  );
}

export default Register;