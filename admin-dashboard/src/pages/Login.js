import React, { useState } from 'react';
import { TextField, Button, Typography, Alert, Box, Link } from '@mui/material';
import { useFormik } from 'formik';
import * as yup from 'yup';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

// Validation schema
const validationSchema = yup.object({
    email: yup
        .string()
        .email('Enter a valid email')
        .required('Email is required'),
    password: yup
        .string()
        .min(6, 'Password should be of minimum 6 characters length')
        .required('Password is required'),
});

const Login = () => {
    const { login } = useAuth();
    const navigate = useNavigate();
    const [error, setError] = useState('');

    const formik = useFormik({
        initialValues: {
            email: '',
            password: '',
        },
        validationSchema: validationSchema,
        onSubmit: async (values) => {
            try {
                await login(values.email, values.password);
                navigate('/dashboard');
            } catch (err) {
                setError(err.response?.data?.detail || 'Failed to login. Please check your credentials.');
            }
        },
    });

    return (
        <>
            <Typography component="h1" variant="h5" align="center" gutterBottom>
                Sign in
            </Typography>

            {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                    {error}
                </Alert>
            )}

            <form onSubmit={formik.handleSubmit}>
                <TextField
                    margin="normal"
                    required
                    fullWidth
                    id="email"
                    label="Email Address"
                    name="email"
                    autoComplete="email"
                    autoFocus
                    value={formik.values.email}
                    onChange={formik.handleChange}
                    error={formik.touched.email && Boolean(formik.errors.email)}
                    helperText={formik.touched.email && formik.errors.email}
                />

                <TextField
                    margin="normal"
                    required
                    fullWidth
                    name="password"
                    label="Password"
                    type="password"
                    id="password"
                    autoComplete="current-password"
                    value={formik.values.password}
                    onChange={formik.handleChange}
                    error={formik.touched.password && Boolean(formik.errors.password)}
                    helperText={formik.touched.password && formik.errors.password}
                />

                <Button
                    type="submit"
                    fullWidth
                    variant="contained"
                    color="primary"
                    sx={{ mt: 3, mb: 2 }}
                    disabled={formik.isSubmitting}
                >
                    {formik.isSubmitting ? 'Signing in...' : 'Sign In'}
                </Button>

                <Box sx={{ textAlign: 'center', mt: 2 }}>
                    <Link href="#" variant="body2" onClick={(e) => {
                        e.preventDefault();
                        alert('Contact your administrator to reset your password.');
                    }}>
                        Forgot password?
                    </Link>
                </Box>
            </form>
        </>
    );
};

export default Login;
