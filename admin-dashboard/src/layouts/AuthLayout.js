import React from 'react';
import { Container, Box, Typography, useTheme as useMuiTheme } from '@mui/material';

const AuthLayout = ({ children }) => {
    const theme = useMuiTheme();

    return (
        <Box
            sx={{
                minHeight: '100vh',
                display: 'flex',
                flexDirection: 'column',
                background: theme.palette.mode === 'light'
                    ? 'linear-gradient(120deg, #e0f7fa 0%, #e8f5e9 100%)'
                    : 'linear-gradient(120deg, #263238 0%, #1a2327 100%)',
            }}
        >
            <Container maxWidth="sm">
                <Box
                    sx={{
                        mt: 8,
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                    }}
                >
                    <Typography
                        variant="h4"
                        component="h1"
                        gutterBottom
                        sx={{
                            fontWeight: 700,
                            color: theme.palette.mode === 'light' ? '#1976d2' : '#90caf9',
                            mb: 4
                        }}
                    >
                        SpaceNew Admin
                    </Typography>
                    <Box
                        sx={{
                            width: '100%',
                            backgroundColor: theme.palette.background.paper,
                            p: 4,
                            borderRadius: 2,
                            boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                        }}
                    >
                        {children}
                    </Box>
                    <Typography
                        variant="body2"
                        color="text.secondary"
                        align="center"
                        sx={{ mt: 4 }}
                    >
                        &copy; {new Date().getFullYear()} SpaceNew. All rights reserved.
                    </Typography>
                </Box>
            </Container>
        </Box>
    );
};

export default AuthLayout;
