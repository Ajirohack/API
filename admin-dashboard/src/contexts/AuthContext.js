import React, { createContext, useContext, useState, useEffect } from 'react';
import authService from '../services/authService';

// Create context
const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [currentUser, setCurrentUser] = useState(null);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        // Check if user is already authenticated
        const checkAuthStatus = async () => {
            try {
                const user = await authService.getCurrentUser();
                if (user) {
                    setCurrentUser(user);
                    setIsAuthenticated(true);
                }
            } catch (err) {
                console.error("Authentication check failed:", err);
                // Clear any stale auth data
                authService.logout();
            } finally {
                setLoading(false);
            }
        };

        checkAuthStatus();
    }, []);

    // Login function
    const login = async (email, password) => {
        setLoading(true);
        setError(null);

        try {
            const user = await authService.login(email, password);
            setCurrentUser(user);
            setIsAuthenticated(true);
            return user;
        } catch (err) {
            setError(err.message || "Login failed");
            throw err;
        } finally {
            setLoading(false);
        }
    };

    // Logout function
    const logout = async () => {
        setLoading(true);

        try {
            await authService.logout();
            setCurrentUser(null);
            setIsAuthenticated(false);
        } catch (err) {
            setError(err.message || "Logout failed");
            console.error("Logout error:", err);
        } finally {
            setLoading(false);
        }
    };

    // Register function
    const register = async (userData) => {
        setLoading(true);
        setError(null);

        try {
            const user = await authService.register(userData);
            return user;
        } catch (err) {
            setError(err.message || "Registration failed");
            throw err;
        } finally {
            setLoading(false);
        }
    };

    const value = {
        currentUser,
        isAuthenticated,
        loading,
        error,
        login,
        logout,
        register
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Custom hook to use the auth context
export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};
