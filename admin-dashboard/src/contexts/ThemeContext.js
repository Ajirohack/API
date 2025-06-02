import React, { createContext, useContext, useState, useMemo } from 'react';
import { ThemeProvider as MuiThemeProvider, createTheme } from '@mui/material/styles';

// Create context
const ThemeContext = createContext(null);

export const ThemeProvider = ({ children }) => {
    const [mode, setMode] = useState(localStorage.getItem('themeMode') || 'light');

    // Generate theme based on current mode
    const theme = useMemo(() => createTheme({
        palette: {
            mode,
            primary: {
                main: '#1976d2',
                light: '#63a4ff',
                dark: '#004ba0',
                contrastText: '#fff',
            },
            secondary: {
                main: '#f50057',
                light: '#ff5983',
                dark: '#bb002f',
                contrastText: '#fff',
            },
            background: {
                default: mode === 'light' ? '#f5f5f5' : '#121212',
                paper: mode === 'light' ? '#ffffff' : '#1e1e1e',
            },
        },
        typography: {
            fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
            h1: {
                fontSize: '2.5rem',
                fontWeight: 500,
            },
            h2: {
                fontSize: '2rem',
                fontWeight: 500,
            },
            h3: {
                fontSize: '1.75rem',
                fontWeight: 500,
            },
            h4: {
                fontSize: '1.5rem',
                fontWeight: 500,
            },
            h5: {
                fontSize: '1.25rem',
                fontWeight: 500,
            },
            h6: {
                fontSize: '1rem',
                fontWeight: 500,
            },
        },
        components: {
            MuiButton: {
                styleOverrides: {
                    root: {
                        textTransform: 'none',
                        borderRadius: 8,
                    },
                },
            },
            MuiCard: {
                styleOverrides: {
                    root: {
                        borderRadius: 12,
                        boxShadow: mode === 'light'
                            ? '0px 2px 4px rgba(0, 0, 0, 0.05), 0px 4px 8px rgba(0, 0, 0, 0.05)'
                            : '0px 2px 4px rgba(0, 0, 0, 0.15), 0px 4px 8px rgba(0, 0, 0, 0.15)',
                    },
                },
            },
        },
    }), [mode]);

    // Toggle theme function
    const toggleTheme = () => {
        const newMode = mode === 'light' ? 'dark' : 'light';
        setMode(newMode);
        localStorage.setItem('themeMode', newMode);
    };

    const value = {
        mode,
        toggleTheme,
    };

    return (
        <ThemeContext.Provider value={value}>
            <MuiThemeProvider theme={theme}>
                {children}
            </MuiThemeProvider>
        </ThemeContext.Provider>
    );
};

// Custom hook to use the theme context
export const useTheme = () => {
    const context = useContext(ThemeContext);
    if (!context) {
        throw new Error('useTheme must be used within a ThemeProvider');
    }
    return context;
};
