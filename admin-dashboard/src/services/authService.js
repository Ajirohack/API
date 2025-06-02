import axios from 'axios';

const API_URL = '/api';

// Add request interceptor to include auth token
axios.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('authToken');
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Add response interceptor to handle common errors
axios.interceptors.response.use(
    (response) => response,
    (error) => {
        // Handle 401 unauthorized by redirecting to login
        if (error.response && error.response.status === 401) {
            localStorage.removeItem('authToken');
            localStorage.removeItem('user');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

const authService = {
    login: async (email, password) => {
        try {
            const response = await axios.post(`${API_URL}/auth/login`, { email, password });
            const { access_token, user } = response.data;

            // Store token and user data
            localStorage.setItem('authToken', access_token);
            localStorage.setItem('user', JSON.stringify(user));

            return user;
        } catch (error) {
            console.error('Login error:', error);
            throw error;
        }
    },

    logout: async () => {
        try {
            await axios.post(`${API_URL}/auth/logout`);
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            // Clear stored data
            localStorage.removeItem('authToken');
            localStorage.removeItem('user');
        }
    },

    register: async (userData) => {
        const response = await axios.post(`${API_URL}/auth/register`, userData);
        return response.data;
    },

    getCurrentUser: async () => {
        const storedUser = localStorage.getItem('user');
        if (!storedUser) return null;

        try {
            // Verify the token is still valid
            const response = await axios.get(`${API_URL}/auth/me`);
            return response.data;
        } catch (error) {
            console.error('Get current user error:', error);
            return null;
        }
    },

    resetPassword: async (email) => {
        const response = await axios.post(`${API_URL}/auth/reset-password`, { email });
        return response.data;
    },

    updatePassword: async (token, password) => {
        const response = await axios.post(`${API_URL}/auth/update-password`, { token, password });
        return response.data;
    }
};

export default authService;
