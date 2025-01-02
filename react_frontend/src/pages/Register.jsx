// Register.js

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { registerUser } from '../api/auth';
import { useForm, Controller } from 'react-hook-form';
import {
  Typography,
  TextField,
  Button,
  Grid,
  Box,
} from '@mui/material';

function Register() {
  const navigate = useNavigate();
  const { handleSubmit, control, watch, formState: { errors } } = useForm();

  const password = watch('password', '');

  const onSubmit = async (data) => {
    try {
      const { email, password, firstname, lastname, institution } = data;
      await registerUser({
        email,
        password,
        firstname,
        lastname,
        institution,
      });
      alert('Registered successfully!');
      navigate('/login');
    } catch (error) {
      console.error(error);
      alert('Registration failed. Check console for details.');
    }
  };

  return (
    <Box sx={{ margin: '2rem' }}>
      <Typography variant="h4" gutterBottom>
        Register
      </Typography>
      <Box component="form" onSubmit={handleSubmit(onSubmit)} noValidate>
        <Grid container spacing={2}>
          {/* Email */}
          <Grid item xs={12}>
            <Controller
              name="email"
              control={control}
              defaultValue=""
              rules={{
                required: 'Email is required',
                pattern: {
                  value: /^\S+@\S+$/i,
                  message: 'Invalid email address',
                },
              }}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="Email"
                  fullWidth
                  required
                  type="email"
                  autoComplete="email"
                  error={!!errors.email}
                  helperText={errors.email ? errors.email.message : ''}
                />
              )}
            />
          </Grid>
          {/* Password */}
          <Grid item xs={12}>
            <Controller
              name="password"
              control={control}
              defaultValue=""
              rules={{ required: 'Password is required' }}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="Password"
                  fullWidth
                  required
                  type="password"
                  autoComplete="new-password"
                  error={!!errors.password}
                  helperText={errors.password ? errors.password.message : ''}
                />
              )}
            />
          </Grid>
          {/* Confirm Password */}
          <Grid item xs={12}>
            <Controller
              name="confirmPassword"
              control={control}
              defaultValue=""
              rules={{
                required: 'Please confirm your password',
                validate: (value) =>
                  value === password || 'Passwords do not match',
              }}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="Confirm Password"
                  fullWidth
                  required
                  type="password"
                  autoComplete="new-password"
                  error={!!errors.confirmPassword}
                  helperText={
                    errors.confirmPassword ? errors.confirmPassword.message : ''
                  }
                />
              )}
            />
          </Grid>
          {/* First Name */}
          <Grid item xs={12} sm={6}>
            <Controller
              name="firstname"
              control={control}
              defaultValue=""
              rules={{ required: 'First name is required' }}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="First Name"
                  fullWidth
                  required
                  autoComplete="given-name"
                  error={!!errors.firstname}
                  helperText={errors.firstname ? errors.firstname.message : ''}
                />
              )}
            />
          </Grid>
          {/* Last Name */}
          <Grid item xs={12} sm={6}>
            <Controller
              name="lastname"
              control={control}
              defaultValue=""
              rules={{ required: 'Last name is required' }}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="Last Name"
                  fullWidth
                  required
                  autoComplete="family-name"
                  error={!!errors.lastname}
                  helperText={errors.lastname ? errors.lastname.message : ''}
                />
              )}
            />
          </Grid>
          {/* Institution */}
          <Grid item xs={12}>
            <Controller
              name="institution"
              control={control}
              defaultValue=""
              rules={{ required: 'Institution is required' }}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="Institution"
                  fullWidth
                  required
                  error={!!errors.institution}
                  helperText={errors.institution ? errors.institution.message : ''}
                />
              )}
            />
          </Grid>
          {/* Submit Button */}
          <Grid item xs={12}>
            <Button type="submit" variant="contained" color="primary" fullWidth>
              Register
            </Button>
          </Grid>
        </Grid>
      </Box>
    </Box>
  );
}

export default Register;