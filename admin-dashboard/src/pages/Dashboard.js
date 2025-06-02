import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Paper,
  Card,
  CardContent,
  CardHeader,
  Avatar,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Divider,
  LinearProgress,
  Chip,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Extension as PluginIcon,
  Schema as WorkflowIcon,
  SmartToy as AgentIcon,
  Storage as RagIcon,
  Info as InfoIcon
} from '@mui/icons-material';

// Import charts
import { Chart as ChartJS, ArcElement, CategoryScale, LinearScale, BarElement, Title, Tooltip as ChartTooltip, Legend } from 'chart.js';
import { Pie, Bar } from 'react-chartjs-2';

ChartJS.register(ArcElement, CategoryScale, LinearScale, BarElement, Title, ChartTooltip, Legend);

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    plugins: { total: 0, active: 0, inactive: 0 },
    workflows: { total: 0, running: 0, completed: 0, failed: 0 },
    agents: { total: 0, active: 0 },
    rag: { documents: 0, totalChunks: 0, avgChunksPerDoc: 0 },
    systemHealth: { healthy: true, services: [] },
    recentActivity: []
  });

  // Simulate loading data from API
  useEffect(() => {
    // Simulated data - in a real app, you'd fetch this from your API
    const loadData = async () => {
      try {
        // Simulate API call delay
        await new Promise(resolve => setTimeout(resolve, 1500));

        // Mock data
        setStats({
          plugins: { total: 8, active: 6, inactive: 2 },
          workflows: { total: 12, running: 3, completed: 7, failed: 2 },
          agents: { total: 5, active: 4 },
          rag: { documents: 156, totalChunks: 2345, avgChunksPerDoc: 15 },
          systemHealth: {
            healthy: true,
            services: [
              { name: 'API Server', status: 'healthy', uptime: '5d 12h' },
              { name: 'Database', status: 'healthy', uptime: '7d 3h' },
              { name: 'RAG Engine', status: 'healthy', uptime: '3d 8h' },
              { name: 'Agent Engine', status: 'healthy', uptime: '3d 8h' }
            ]
          },
          recentActivity: [
            { id: 1, type: 'workflow', name: 'Data Processing', status: 'completed', time: '10 minutes ago' },
            { id: 2, type: 'agent', name: 'Customer Support Bot', status: 'active', time: '25 minutes ago' },
            { id: 3, type: 'rag', name: 'Knowledge Base Update', status: 'completed', time: '1 hour ago' },
            { id: 4, type: 'workflow', name: 'Email Campaign', status: 'failed', time: '2 hours ago' },
            { id: 5, type: 'plugin', name: 'Analytics Plugin', status: 'installed', time: '3 hours ago' }
          ]
        });
      } catch (error) {
        console.error('Error loading dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  const handleRefresh = () => {
    setLoading(true);
    // Re-fetch data (in a real app)
    setTimeout(() => setLoading(false), 1000);
  };

  // Chart data
  const pluginChartData = {
    labels: ['Active', 'Inactive'],
    datasets: [
      {
        data: [stats.plugins.active, stats.plugins.inactive],
        backgroundColor: ['rgba(54, 162, 235, 0.8)', 'rgba(255, 99, 132, 0.8)'],
        borderColor: ['rgba(54, 162, 235, 1)', 'rgba(255, 99, 132, 1)'],
        borderWidth: 1,
      },
    ],
  };

  const workflowChartData = {
    labels: ['Running', 'Completed', 'Failed'],
    datasets: [
      {
        label: 'Workflows',
        data: [stats.workflows.running, stats.workflows.completed, stats.workflows.failed],
        backgroundColor: [
          'rgba(255, 206, 86, 0.8)',
          'rgba(75, 192, 192, 0.8)',
          'rgba(255, 99, 132, 0.8)',
        ],
      },
    ],
  };

  const workflowChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Workflow Status',
      },
    },
  };

  if (loading) {
    return (
      <Box sx={{ width: '100%', mt: 4 }}>
        <Typography variant="h4" gutterBottom>
          Dashboard
        </Typography>
        <LinearProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Dashboard</Typography>
        <Tooltip title="Refresh data">
          <IconButton onClick={handleRefresh}>
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Summary Statistics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Paper elevation={2} sx={{ p: 2, display: 'flex', alignItems: 'center' }}>
            <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
              <PluginIcon />
            </Avatar>
            <Box>
              <Typography variant="body2" color="text.secondary">
                Plugins
              </Typography>
              <Typography variant="h5">
                {stats.plugins.total}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {stats.plugins.active} active
              </Typography>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Paper elevation={2} sx={{ p: 2, display: 'flex', alignItems: 'center' }}>
            <Avatar sx={{ bgcolor: 'secondary.main', mr: 2 }}>
              <WorkflowIcon />
            </Avatar>
            <Box>
              <Typography variant="body2" color="text.secondary">
                Workflows
              </Typography>
              <Typography variant="h5">
                {stats.workflows.total}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {stats.workflows.running} running
              </Typography>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Paper elevation={2} sx={{ p: 2, display: 'flex', alignItems: 'center' }}>
            <Avatar sx={{ bgcolor: 'success.main', mr: 2 }}>
              <AgentIcon />
            </Avatar>
            <Box>
              <Typography variant="body2" color="text.secondary">
                Agents
              </Typography>
              <Typography variant="h5">
                {stats.agents.total}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {stats.agents.active} active
              </Typography>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Paper elevation={2} sx={{ p: 2, display: 'flex', alignItems: 'center' }}>
            <Avatar sx={{ bgcolor: 'info.main', mr: 2 }}>
              <RagIcon />
            </Avatar>
            <Box>
              <Typography variant="body2" color="text.secondary">
                RAG Documents
              </Typography>
              <Typography variant="h5">
                {stats.rag.documents}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {stats.rag.totalChunks} chunks
              </Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Charts and Detailed Info */}
      <Grid container spacing={3}>
        {/* Plugin Chart */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardHeader title="Plugin Status" />
            <CardContent>
              <Box sx={{ height: 240, display: 'flex', justifyContent: 'center' }}>
                <Pie data={pluginChartData} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Workflow Chart */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardHeader title="Workflow Distribution" />
            <CardContent>
              <Box sx={{ height: 240 }}>
                <Bar options={workflowChartOptions} data={workflowChartData} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* System Health */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              title="System Health"
              action={
                <Tooltip title="All services operational">
                  <IconButton>
                    <InfoIcon />
                  </IconButton>
                </Tooltip>
              }
            />
            <CardContent>
              <List>
                {stats.systemHealth.services.map((service, index) => (
                  <React.Fragment key={service.name}>
                    {index > 0 && <Divider component="li" />}
                    <ListItem secondaryAction={
                      <Chip
                        label={service.status}
                        color={service.status === 'healthy' ? 'success' : 'error'}
                        size="small"
                      />
                    }>
                      <ListItemText
                        primary={service.name}
                        secondary={`Uptime: ${service.uptime}`}
                      />
                    </ListItem>
                  </React.Fragment>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="Recent Activity" />
            <CardContent>
              <List>
                {stats.recentActivity.map((activity, index) => (
                  <React.Fragment key={activity.id}>
                    {index > 0 && <Divider component="li" />}
                    <ListItem>
                      <ListItemAvatar>
                        <Avatar>
                          {activity.type === 'workflow' && <WorkflowIcon />}
                          {activity.type === 'agent' && <AgentIcon />}
                          {activity.type === 'rag' && <RagIcon />}
                          {activity.type === 'plugin' && <PluginIcon />}
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary={activity.name}
                        secondary={`${activity.status} · ${activity.time}`}
                      />
                    </ListItem>
                  </React.Fragment>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
