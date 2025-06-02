import React from 'react';
import { Box, Typography, Container, Button, Paper } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const NotFound = () => {
  const navigate = useNavigate();

  return (
    <Container maxWidth="md">
      <Paper
        sx={{
          mt: 8,
          p: 4,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          textAlign: 'center',
        }}
        elevation={3}
      >
        <Typography variant="h1" component="h1" sx={{ fontSize: 120, fontWeight: 700, color: 'text.secondary' }}>
          404
        </Typography>

        <Typography variant="h4" component="h2" gutterBottom>
          Page Not Found
        </Typography>

        <Typography variant="body1" color="text.secondary" paragraph sx={{ maxWidth: 500 }}>
          The page you are looking for doesn't exist or has been moved.
          Please check the URL or navigate back to the dashboard.
        </Typography>

        <Box sx={{ mt: 4 }}>
          <Button
            variant="contained"
            color="primary"
            size="large"
            onClick={() => navigate('/dashboard')}
          >
            Go to Dashboard
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default NotFound;
