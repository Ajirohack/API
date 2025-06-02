import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { CssBaseline } from '@mui/material';

// Layouts
import DashboardLayout from './layouts/DashboardLayout';
import AuthLayout from './layouts/AuthLayout';

// Pages
import Dashboard from './pages/Dashboard';
import Plugins from './pages/Plugins';
import Workflows from './pages/Workflows';
import WorkflowBuilder from './pages/WorkflowBuilder';
import Agents from './pages/Agents';
import RagDashboard from './pages/RagDashboard';
import Settings from './pages/Settings';
import Login from './pages/Login';
import NotFound from './pages/NotFound';

// Contexts
import { useAuth } from './contexts/AuthContext';

function App() {
    const { isAuthenticated, loading } = useAuth();

    // Show loading indicator while checking authentication
    if (loading) {
        return <div>Loading...</div>
    }

    return (
        <>
            <CssBaseline />
            <Routes>
                {/* Public routes */}
                <Route path="/login" element={
                    isAuthenticated ? <Navigate to="/dashboard" replace /> : <AuthLayout><Login /></AuthLayout>
                } />

                {/* Protected routes */}
                <Route path="/dashboard" element={
                    isAuthenticated ? <DashboardLayout><Dashboard /></DashboardLayout> : <Navigate to="/login" replace />
                } />
                <Route path="/plugins" element={
                    isAuthenticated ? <DashboardLayout><Plugins /></DashboardLayout> : <Navigate to="/login" replace />
                } />
                <Route path="/workflows" element={
                    isAuthenticated ? <DashboardLayout><Workflows /></DashboardLayout> : <Navigate to="/login" replace />
                } />
                <Route path="/workflows/builder" element={
                    isAuthenticated ? <DashboardLayout><WorkflowBuilder /></DashboardLayout> : <Navigate to="/login" replace />
                } />
                <Route path="/workflows/builder/:id" element={
                    isAuthenticated ? <DashboardLayout><WorkflowBuilder /></DashboardLayout> : <Navigate to="/login" replace />
                } />
                <Route path="/agents" element={
                    isAuthenticated ? <DashboardLayout><Agents /></DashboardLayout> : <Navigate to="/login" replace />
                } />
                <Route path="/rag" element={
                    isAuthenticated ? <DashboardLayout><RagDashboard /></DashboardLayout> : <Navigate to="/login" replace />
                } />
                <Route path="/settings" element={
                    isAuthenticated ? <DashboardLayout><Settings /></DashboardLayout> : <Navigate to="/login" replace />
                } />

                {/* Default routes */}
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                <Route path="*" element={<NotFound />} />
            </Routes>
        </>
    );
}

export default App;
