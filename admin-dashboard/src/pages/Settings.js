import React, { useState, useEffect } from 'react';
import {
    Box,
    Typography,
    Paper,
    Grid,
    Card,
    CardContent,
    CardHeader,
    Divider,
    TextField,
    Button,
    List,
    ListItem,
    ListItemText,
    ListItemSecondaryAction,
    Switch,
    FormControl,
    FormControlLabel,
    RadioGroup,
    Radio,
    Alert,
    Tabs,
    Tab,
    InputLabel,
    Select,
    MenuItem,
    IconButton,
    Snackbar,
    CircularProgress,
} from '@mui/material';
import {
    Save as SaveIcon,
    Refresh as RefreshIcon,
    Delete as DeleteIcon,
    Add as AddIcon,
    Edit as EditIcon,
    Download as DownloadIcon,
    Security as SecurityIcon,
    Storage as DatabaseIcon,
    Notifications as NotificationsIcon,
    PermIdentity as UserIcon,
    LightMode as LightModeIcon,
    DarkMode as DarkModeIcon,
    Tune as TuneIcon
} from '@mui/icons-material';

import { useTheme } from '../contexts/ThemeContext';

// Tab Panel component
function TabPanel(props) {
    const { children, value, index, ...other } = props;

    return (
        <div
            role="tabpanel"
            hidden={value !== index}
            id={`settings-tabpanel-${index}`}
            aria-labelledby={`settings-tab-${index}`}
            {...other}
        >
            {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
        </div>
    );
}

const Settings = () => {
    const { mode, toggleColorMode } = useTheme();
    const [tabValue, setTabValue] = useState(0);
    const [saving, setSaving] = useState(false);
    const [snackbar, setSnackbar] = useState({
        open: false,
        message: '',
        severity: 'success',
    });

    // General settings state
    const [generalSettings, setGeneralSettings] = useState({
        systemName: 'SpaceNew',
        environment: 'production',
        loggingLevel: 'info',
        maxConcurrentTasks: 10,
        enableAnalytics: true,
        enableHealthMonitoring: true,
        timezone: 'UTC',
    });

    // API settings state
    const [apiSettings, setApiSettings] = useState({
        apiRateLimit: 100,
        apiTokenExpiration: 86400,
        enableRateLimiting: true,
        apiDocumentation: true,
        corsAllowedOrigins: '*',
        maxRequestSize: 10,
    });

    // Database settings
    const [databaseSettings, setDatabaseSettings] = useState({
        connectionPool: 20,
        queryTimeout: 30,
        enableQueryLogging: false,
        backupSchedule: 'daily',
    });

    // Notification settings
    const [notificationSettings, setNotificationSettings] = useState({
        emailNotifications: true,
        slackIntegration: false,
        slackWebhook: '',
        criticalAlertsOnly: false,
        alertChannels: ['email'],
        enableSystemNotifications: true,
    });

    const handleTabChange = (event, newValue) => {
        setTabValue(newValue);
    };

    const updateGeneralSettings = (key, value) => {
        setGeneralSettings({
            ...generalSettings,
            [key]: value,
        });
    };

    const updateApiSettings = (key, value) => {
        setApiSettings({
            ...apiSettings,
            [key]: value,
        });
    };

    const updateDatabaseSettings = (key, value) => {
        setDatabaseSettings({
            ...databaseSettings,
            [key]: value,
        });
    };

    const updateNotificationSettings = (key, value) => {
        setNotificationSettings({
            ...notificationSettings,
            [key]: value,
        });
    };

    const handleSaveSettings = async () => {
        setSaving(true);

        try {
            // In a real app, this would save to an API
            // await settingsService.saveSettings({ 
            //   general: generalSettings,
            //   api: apiSettings,
            //   database: databaseSettings,
            //   notification: notificationSettings 
            // });

            // Simulate API delay
            await new Promise(resolve => setTimeout(resolve, 1000));

            setSnackbar({
                open: true,
                message: 'Settings saved successfully',
                severity: 'success',
            });
        } catch (error) {
            console.error('Error saving settings:', error);
            setSnackbar({
                open: true,
                message: 'Failed to save settings',
                severity: 'error',
            });
        } finally {
            setSaving(false);
        }
    };

    const handleCloseSnackbar = () => {
        setSnackbar({
            ...snackbar,
            open: false,
        });
    };

    return (
        <Box>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Typography variant="h4" component="h1">
                    System Settings
                </Typography>
                <Box>
                    <Button
                        variant="contained"
                        color="primary"
                        startIcon={saving ? <CircularProgress size={20} color="inherit" /> : <SaveIcon />}
                        onClick={handleSaveSettings}
                        disabled={saving}
                    >
                        {saving ? 'Saving...' : 'Save Settings'}
                    </Button>
                </Box>
            </Box>

            <Paper sx={{ mb: 3 }}>
                <Tabs
                    value={tabValue}
                    onChange={handleTabChange}
                    indicatorColor="primary"
                    textColor="primary"
                    variant="scrollable"
                    scrollButtons="auto"
                    sx={{ borderBottom: 1, borderColor: 'divider' }}
                >
                    <Tab icon={<TuneIcon />} iconPosition="start" label="General" />
                    <Tab icon={<SecurityIcon />} iconPosition="start" label="API & Security" />
                    <Tab icon={<DatabaseIcon />} iconPosition="start" label="Database" />
                    <Tab icon={<NotificationsIcon />} iconPosition="start" label="Notifications" />
                    <Tab icon={<UserIcon />} iconPosition="start" label="User Interface" />
                </Tabs>

                {/* General Settings */}
                <TabPanel value={tabValue} index={0}>
                    <Grid container spacing={3}>
                        <Grid item xs={12} md={6}>
                            <Card>
                                <CardHeader title="Basic Settings" />
                                <Divider />
                                <CardContent>
                                    <Grid container spacing={2}>
                                        <Grid item xs={12}>
                                            <TextField
                                                label="System Name"
                                                fullWidth
                                                value={generalSettings.systemName}
                                                onChange={(e) => updateGeneralSettings('systemName', e.target.value)}
                                            />
                                        </Grid>
                                        <Grid item xs={12}>
                                            <FormControl fullWidth>
                                                <InputLabel>Environment</InputLabel>
                                                <Select
                                                    value={generalSettings.environment}
                                                    label="Environment"
                                                    onChange={(e) => updateGeneralSettings('environment', e.target.value)}
                                                >
                                                    <MenuItem value="development">Development</MenuItem>
                                                    <MenuItem value="staging">Staging</MenuItem>
                                                    <MenuItem value="production">Production</MenuItem>
                                                </Select>
                                            </FormControl>
                                        </Grid>
                                        <Grid item xs={12}>
                                            <FormControl fullWidth>
                                                <InputLabel>Logging Level</InputLabel>
                                                <Select
                                                    value={generalSettings.loggingLevel}
                                                    label="Logging Level"
                                                    onChange={(e) => updateGeneralSettings('loggingLevel', e.target.value)}
                                                >
                                                    <MenuItem value="debug">Debug</MenuItem>
                                                    <MenuItem value="info">Info</MenuItem>
                                                    <MenuItem value="warn">Warning</MenuItem>
                                                    <MenuItem value="error">Error</MenuItem>
                                                </Select>
                                            </FormControl>
                                        </Grid>
                                        <Grid item xs={12}>
                                            <TextField
                                                label="Max Concurrent Tasks"
                                                type="number"
                                                fullWidth
                                                value={generalSettings.maxConcurrentTasks}
                                                onChange={(e) => updateGeneralSettings('maxConcurrentTasks', parseInt(e.target.value))}
                                            />
                                        </Grid>
                                        <Grid item xs={12}>
                                            <FormControl fullWidth>
                                                <InputLabel>Timezone</InputLabel>
                                                <Select
                                                    value={generalSettings.timezone}
                                                    label="Timezone"
                                                    onChange={(e) => updateGeneralSettings('timezone', e.target.value)}
                                                >
                                                    <MenuItem value="UTC">UTC</MenuItem>
                                                    <MenuItem value="America/New_York">Eastern Time (ET)</MenuItem>
                                                    <MenuItem value="America/Chicago">Central Time (CT)</MenuItem>
                                                    <MenuItem value="America/Denver">Mountain Time (MT)</MenuItem>
                                                    <MenuItem value="America/Los_Angeles">Pacific Time (PT)</MenuItem>
                                                    <MenuItem value="Europe/London">London</MenuItem>
                                                    <MenuItem value="Asia/Tokyo">Tokyo</MenuItem>
                                                </Select>
                                            </FormControl>
                                        </Grid>
                                    </Grid>
                                </CardContent>
                            </Card>
                        </Grid>

                        <Grid item xs={12} md={6}>
                            <Card>
                                <CardHeader title="Features" />
                                <Divider />
                                <CardContent>
                                    <List>
                                        <ListItem>
                                            <ListItemText
                                                primary="Analytics"
                                                secondary="Collect anonymous usage data to improve the system"
                                            />
                                            <ListItemSecondaryAction>
                                                <Switch
                                                    edge="end"
                                                    checked={generalSettings.enableAnalytics}
                                                    onChange={(e) => updateGeneralSettings('enableAnalytics', e.target.checked)}
                                                />
                                            </ListItemSecondaryAction>
                                        </ListItem>
                                        <Divider component="li" />
                                        <ListItem>
                                            <ListItemText
                                                primary="Health Monitoring"
                                                secondary="Monitor system health and performance"
                                            />
                                            <ListItemSecondaryAction>
                                                <Switch
                                                    edge="end"
                                                    checked={generalSettings.enableHealthMonitoring}
                                                    onChange={(e) => updateGeneralSettings('enableHealthMonitoring', e.target.checked)}
                                                />
                                            </ListItemSecondaryAction>
                                        </ListItem>
                                    </List>
                                </CardContent>
                            </Card>

                            <Card sx={{ mt: 3 }}>
                                <CardHeader title="System Maintenance" />
                                <Divider />
                                <CardContent>
                                    <Alert severity="info" sx={{ mb: 2 }}>
                                        Regular maintenance ensures optimal system performance.
                                    </Alert>
                                    <Grid container spacing={2}>
                                        <Grid item xs={12}>
                                            <Button
                                                variant="outlined"
                                                fullWidth
                                                startIcon={<RefreshIcon />}
                                            >
                                                Clear System Cache
                                            </Button>
                                        </Grid>
                                        <Grid item xs={12}>
                                            <Button
                                                variant="outlined"
                                                fullWidth
                                                startIcon={<DownloadIcon />}
                                            >
                                                Download System Logs
                                            </Button>
                                        </Grid>
                                    </Grid>
                                </CardContent>
                            </Card>
                        </Grid>
                    </Grid>
                </TabPanel>

                {/* API & Security Settings */}
                <TabPanel value={tabValue} index={1}>
                    <Grid container spacing={3}>
                        <Grid item xs={12} md={6}>
                            <Card>
                                <CardHeader title="API Settings" />
                                <Divider />
                                <CardContent>
                                    <Grid container spacing={2}>
                                        <Grid item xs={12}>
                                            <TextField
                                                label="API Rate Limit (requests per minute)"
                                                type="number"
                                                fullWidth
                                                value={apiSettings.apiRateLimit}
                                                onChange={(e) => updateApiSettings('apiRateLimit', parseInt(e.target.value))}
                                            />
                                        </Grid>
                                        <Grid item xs={12}>
                                            <TextField
                                                label="API Token Expiration (seconds)"
                                                type="number"
                                                fullWidth
                                                value={apiSettings.apiTokenExpiration}
                                                onChange={(e) => updateApiSettings('apiTokenExpiration', parseInt(e.target.value))}
                                            />
                                        </Grid>
                                        <Grid item xs={12}>
                                            <TextField
                                                label="CORS Allowed Origins"
                                                fullWidth
                                                value={apiSettings.corsAllowedOrigins}
                                                onChange={(e) => updateApiSettings('corsAllowedOrigins', e.target.value)}
                                                helperText="Use * for all origins or comma-separated list of domains"
                                            />
                                        </Grid>
                                        <Grid item xs={12}>
                                            <TextField
                                                label="Max Request Size (MB)"
                                                type="number"
                                                fullWidth
                                                value={apiSettings.maxRequestSize}
                                                onChange={(e) => updateApiSettings('maxRequestSize', parseInt(e.target.value))}
                                            />
                                        </Grid>
                                    </Grid>

                                    <List sx={{ mt: 2 }}>
                                        <ListItem>
                                            <ListItemText
                                                primary="Enable Rate Limiting"
                                                secondary="Limit the number of requests from a single client"
                                            />
                                            <ListItemSecondaryAction>
                                                <Switch
                                                    edge="end"
                                                    checked={apiSettings.enableRateLimiting}
                                                    onChange={(e) => updateApiSettings('enableRateLimiting', e.target.checked)}
                                                />
                                            </ListItemSecondaryAction>
                                        </ListItem>
                                        <Divider component="li" />
                                        <ListItem>
                                            <ListItemText
                                                primary="API Documentation"
                                                secondary="Expose API documentation (OpenAPI/Swagger)"
                                            />
                                            <ListItemSecondaryAction>
                                                <Switch
                                                    edge="end"
                                                    checked={apiSettings.apiDocumentation}
                                                    onChange={(e) => updateApiSettings('apiDocumentation', e.target.checked)}
                                                />
                                            </ListItemSecondaryAction>
                                        </ListItem>
                                    </List>
                                </CardContent>
                            </Card>
                        </Grid>

                        <Grid item xs={12} md={6}>
                            <Card>
                                <CardHeader title="Security Settings" />
                                <Divider />
                                <CardContent>
                                    <Alert severity="warning" sx={{ mb: 3 }}>
                                        Changes to security settings may require system restart
                                    </Alert>

                                    <Typography variant="subtitle2" gutterBottom>
                                        Authentication Methods
                                    </Typography>
                                    <FormControl component="fieldset">
                                        <RadioGroup defaultValue="jwt">
                                            <FormControlLabel value="jwt" control={<Radio />} label="JWT Authentication" />
                                            <FormControlLabel value="oauth" control={<Radio />} label="OAuth 2.0" />
                                            <FormControlLabel value="apikey" control={<Radio />} label="API Key" />
                                        </RadioGroup>
                                    </FormControl>

                                    <Typography variant="subtitle2" gutterBottom sx={{ mt: 3 }}>
                                        Password Policy
                                    </Typography>
                                    <List dense>
                                        <ListItem>
                                            <ListItemText
                                                primary="Minimum password length"
                                                secondary="8 characters"
                                            />
                                            <ListItemSecondaryAction>
                                                <IconButton edge="end" size="small">
                                                    <EditIcon fontSize="small" />
                                                </IconButton>
                                            </ListItemSecondaryAction>
                                        </ListItem>
                                        <ListItem>
                                            <ListItemText
                                                primary="Require special characters"
                                                secondary="Enabled"
                                            />
                                            <ListItemSecondaryAction>
                                                <Switch edge="end" size="small" defaultChecked />
                                            </ListItemSecondaryAction>
                                        </ListItem>
                                        <ListItem>
                                            <ListItemText
                                                primary="Password expiration"
                                                secondary="90 days"
                                            />
                                            <ListItemSecondaryAction>
                                                <IconButton edge="end" size="small">
                                                    <EditIcon fontSize="small" />
                                                </IconButton>
                                            </ListItemSecondaryAction>
                                        </ListItem>
                                    </List>
                                </CardContent>
                            </Card>

                            <Card sx={{ mt: 3 }}>
                                <CardHeader title="API Keys" />
                                <Divider />
                                <CardContent>
                                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                                        <Typography variant="subtitle2">
                                            Active API Keys: 3
                                        </Typography>
                                        <Button
                                            startIcon={<AddIcon />}
                                            size="small"
                                        >
                                            Generate New Key
                                        </Button>
                                    </Box>
                                    <List dense>
                                        <ListItem>
                                            <ListItemText
                                                primary="Production Key"
                                                secondary="Last used: 2 hours ago"
                                            />
                                            <ListItemSecondaryAction>
                                                <IconButton edge="end" size="small" color="error">
                                                    <DeleteIcon fontSize="small" />
                                                </IconButton>
                                            </ListItemSecondaryAction>
                                        </ListItem>
                                        <ListItem>
                                            <ListItemText
                                                primary="Development Key"
                                                secondary="Last used: 1 day ago"
                                            />
                                            <ListItemSecondaryAction>
                                                <IconButton edge="end" size="small" color="error">
                                                    <DeleteIcon fontSize="small" />
                                                </IconButton>
                                            </ListItemSecondaryAction>
                                        </ListItem>
                                        <ListItem>
                                            <ListItemText
                                                primary="Testing Key"
                                                secondary="Last used: 5 days ago"
                                            />
                                            <ListItemSecondaryAction>
                                                <IconButton edge="end" size="small" color="error">
                                                    <DeleteIcon fontSize="small" />
                                                </IconButton>
                                            </ListItemSecondaryAction>
                                        </ListItem>
                                    </List>
                                </CardContent>
                            </Card>
                        </Grid>
                    </Grid>
                </TabPanel>

                {/* Database Settings */}
                <TabPanel value={tabValue} index={2}>
                    <Grid container spacing={3}>
                        <Grid item xs={12} md={6}>
                            <Card>
                                <CardHeader title="Database Configuration" />
                                <Divider />
                                <CardContent>
                                    <Grid container spacing={2}>
                                        <Grid item xs={12}>
                                            <TextField
                                                label="Connection Pool Size"
                                                type="number"
                                                fullWidth
                                                value={databaseSettings.connectionPool}
                                                onChange={(e) => updateDatabaseSettings('connectionPool', parseInt(e.target.value))}
                                            />
                                        </Grid>
                                        <Grid item xs={12}>
                                            <TextField
                                                label="Query Timeout (seconds)"
                                                type="number"
                                                fullWidth
                                                value={databaseSettings.queryTimeout}
                                                onChange={(e) => updateDatabaseSettings('queryTimeout', parseInt(e.target.value))}
                                            />
                                        </Grid>
                                        <Grid item xs={12}>
                                            <FormControl fullWidth>
                                                <InputLabel>Backup Schedule</InputLabel>
                                                <Select
                                                    value={databaseSettings.backupSchedule}
                                                    label="Backup Schedule"
                                                    onChange={(e) => updateDatabaseSettings('backupSchedule', e.target.value)}
                                                >
                                                    <MenuItem value="hourly">Hourly</MenuItem>
                                                    <MenuItem value="daily">Daily</MenuItem>
                                                    <MenuItem value="weekly">Weekly</MenuItem>
                                                    <MenuItem value="monthly">Monthly</MenuItem>
                                                </Select>
                                            </FormControl>
                                        </Grid>
                                    </Grid>

                                    <List sx={{ mt: 2 }}>
                                        <ListItem>
                                            <ListItemText
                                                primary="Query Logging"
                                                secondary="Log database queries for debugging"
                                            />
                                            <ListItemSecondaryAction>
                                                <Switch
                                                    edge="end"
                                                    checked={databaseSettings.enableQueryLogging}
                                                    onChange={(e) => updateDatabaseSettings('enableQueryLogging', e.target.checked)}
                                                />
                                            </ListItemSecondaryAction>
                                        </ListItem>
                                    </List>
                                </CardContent>
                            </Card>
                        </Grid>

                        <Grid item xs={12} md={6}>
                            <Card>
                                <CardHeader title="Database Operations" />
                                <Divider />
                                <CardContent>
                                    <Alert severity="warning" sx={{ mb: 3 }}>
                                        Database operations can affect system performance. Use with caution.
                                    </Alert>

                                    <Grid container spacing={2}>
                                        <Grid item xs={12}>
                                            <Button
                                                variant="outlined"
                                                fullWidth
                                                startIcon={<DownloadIcon />}
                                            >
                                                Backup Database Now
                                            </Button>
                                        </Grid>
                                        <Grid item xs={12}>
                                            <Button
                                                variant="outlined"
                                                fullWidth
                                                startIcon={<RefreshIcon />}
                                            >
                                                Optimize Database
                                            </Button>
                                        </Grid>
                                        <Grid item xs={12}>
                                            <Button
                                                variant="outlined"
                                                color="error"
                                                fullWidth
                                            >
                                                Reset Test Data
                                            </Button>
                                        </Grid>
                                    </Grid>
                                </CardContent>
                            </Card>

                            <Card sx={{ mt: 3 }}>
                                <CardHeader title="Database Statistics" />
                                <Divider />
                                <CardContent>
                                    <List dense>
                                        <ListItem>
                                            <ListItemText
                                                primary="Total Size"
                                                secondary="1.2 GB"
                                            />
                                        </ListItem>
                                        <ListItem>
                                            <ListItemText
                                                primary="Number of Tables"
                                                secondary="27"
                                            />
                                        </ListItem>
                                        <ListItem>
                                            <ListItemText
                                                primary="Last Backup"
                                                secondary="2024-04-15 01:00:00"
                                            />
                                        </ListItem>
                                        <ListItem>
                                            <ListItemText
                                                primary="Index Size"
                                                secondary="320 MB"
                                            />
                                        </ListItem>
                                        <ListItem>
                                            <ListItemText
                                                primary="Active Connections"
                                                secondary="5 / 20"
                                            />
                                        </ListItem>
                                    </List>
                                </CardContent>
                            </Card>
                        </Grid>
                    </Grid>
                </TabPanel>

                {/* Notification Settings */}
                <TabPanel value={tabValue} index={3}>
                    <Grid container spacing={3}>
                        <Grid item xs={12} md={6}>
                            <Card>
                                <CardHeader title="Alert Settings" />
                                <Divider />
                                <CardContent>
                                    <List>
                                        <ListItem>
                                            <ListItemText
                                                primary="Email Notifications"
                                                secondary="Send system alerts via email"
                                            />
                                            <ListItemSecondaryAction>
                                                <Switch
                                                    edge="end"
                                                    checked={notificationSettings.emailNotifications}
                                                    onChange={(e) => updateNotificationSettings('emailNotifications', e.target.checked)}
                                                />
                                            </ListItemSecondaryAction>
                                        </ListItem>
                                        <Divider component="li" />
                                        <ListItem>
                                            <ListItemText
                                                primary="Slack Integration"
                                                secondary="Send notifications to Slack"
                                            />
                                            <ListItemSecondaryAction>
                                                <Switch
                                                    edge="end"
                                                    checked={notificationSettings.slackIntegration}
                                                    onChange={(e) => updateNotificationSettings('slackIntegration', e.target.checked)}
                                                />
                                            </ListItemSecondaryAction>
                                        </ListItem>
                                        {notificationSettings.slackIntegration && (
                                            <ListItem sx={{ pl: 4 }}>
                                                <TextField
                                                    label="Slack Webhook URL"
                                                    fullWidth
                                                    value={notificationSettings.slackWebhook}
                                                    onChange={(e) => updateNotificationSettings('slackWebhook', e.target.value)}
                                                />
                                            </ListItem>
                                        )}
                                        <Divider component="li" />
                                        <ListItem>
                                            <ListItemText
                                                primary="Critical Alerts Only"
                                                secondary="Only send notifications for critical issues"
                                            />
                                            <ListItemSecondaryAction>
                                                <Switch
                                                    edge="end"
                                                    checked={notificationSettings.criticalAlertsOnly}
                                                    onChange={(e) => updateNotificationSettings('criticalAlertsOnly', e.target.checked)}
                                                />
                                            </ListItemSecondaryAction>
                                        </ListItem>
                                        <Divider component="li" />
                                        <ListItem>
                                            <ListItemText
                                                primary="System Notifications"
                                                secondary="Show notifications in admin dashboard"
                                            />
                                            <ListItemSecondaryAction>
                                                <Switch
                                                    edge="end"
                                                    checked={notificationSettings.enableSystemNotifications}
                                                    onChange={(e) => updateNotificationSettings('enableSystemNotifications', e.target.checked)}
                                                />
                                            </ListItemSecondaryAction>
                                        </ListItem>
                                    </List>
                                </CardContent>
                            </Card>
                        </Grid>

                        <Grid item xs={12} md={6}>
                            <Card>
                                <CardHeader title="Notification Recipients" />
                                <Divider />
                                <CardContent>
                                    <List dense>
                                        <ListItem>
                                            <ListItemText
                                                primary="System Administrator"
                                                secondary="admin@example.com"
                                            />
                                            <ListItemSecondaryAction>
                                                <IconButton edge="end" size="small">
                                                    <EditIcon fontSize="small" />
                                                </IconButton>
                                            </ListItemSecondaryAction>
                                        </ListItem>
                                        <ListItem>
                                            <ListItemText
                                                primary="Technical Support"
                                                secondary="support@example.com"
                                            />
                                            <ListItemSecondaryAction>
                                                <IconButton edge="end" size="small">
                                                    <EditIcon fontSize="small" />
                                                </IconButton>
                                            </ListItemSecondaryAction>
                                        </ListItem>
                                        <ListItem>
                                            <ListItemText
                                                primary="Operations Team"
                                                secondary="operations@example.com"
                                            />
                                            <ListItemSecondaryAction>
                                                <IconButton edge="end" size="small">
                                                    <EditIcon fontSize="small" />
                                                </IconButton>
                                            </ListItemSecondaryAction>
                                        </ListItem>
                                    </List>

                                    <Button
                                        startIcon={<AddIcon />}
                                        sx={{ mt: 2 }}
                                    >
                                        Add Recipient
                                    </Button>
                                </CardContent>
                            </Card>

                            <Card sx={{ mt: 3 }}>
                                <CardHeader title="Test Notifications" />
                                <Divider />
                                <CardContent>
                                    <Alert severity="info" sx={{ mb: 2 }}>
                                        Send test notifications to verify your configuration.
                                    </Alert>

                                    <Grid container spacing={2}>
                                        <Grid item xs={12}>
                                            <Button
                                                variant="outlined"
                                                fullWidth
                                            >
                                                Send Test Email
                                            </Button>
                                        </Grid>
                                        <Grid item xs={12}>
                                            <Button
                                                variant="outlined"
                                                fullWidth
                                                disabled={!notificationSettings.slackIntegration}
                                            >
                                                Send Test Slack Message
                                            </Button>
                                        </Grid>
                                    </Grid>
                                </CardContent>
                            </Card>
                        </Grid>
                    </Grid>
                </TabPanel>

                {/* User Interface Settings */}
                <TabPanel value={tabValue} index={4}>
                    <Grid container spacing={3}>
                        <Grid item xs={12} md={6}>
                            <Card>
                                <CardHeader title="Theme Settings" />
                                <Divider />
                                <CardContent>
                                    <Typography variant="subtitle2" gutterBottom>
                                        Color Theme
                                    </Typography>
                                    <Box display="flex" gap={2} mb={3}>
                                        <Card
                                            variant="outlined"
                                            sx={{
                                                p: 2,
                                                width: '50%',
                                                cursor: 'pointer',
                                                bgcolor: mode === 'light' ? 'primary.main' : 'inherit',
                                                color: mode === 'light' ? 'white' : 'inherit',
                                            }}
                                            onClick={() => mode !== 'light' && toggleColorMode()}
                                        >
                                            <Box display="flex" alignItems="center" justifyContent="center" flexDirection="column">
                                                <LightModeIcon sx={{ fontSize: 40, mb: 1 }} />
                                                <Typography>Light Mode</Typography>
                                            </Box>
                                        </Card>

                                        <Card
                                            variant="outlined"
                                            sx={{
                                                p: 2,
                                                width: '50%',
                                                cursor: 'pointer',
                                                bgcolor: mode === 'dark' ? 'primary.main' : 'inherit',
                                                color: mode === 'dark' ? 'white' : 'inherit',
                                            }}
                                            onClick={() => mode !== 'dark' && toggleColorMode()}
                                        >
                                            <Box display="flex" alignItems="center" justifyContent="center" flexDirection="column">
                                                <DarkModeIcon sx={{ fontSize: 40, mb: 1 }} />
                                                <Typography>Dark Mode</Typography>
                                            </Box>
                                        </Card>
                                    </Box>

                                    <Typography variant="subtitle2" gutterBottom>
                                        Default Dashboard
                                    </Typography>
                                    <FormControl component="fieldset">
                                        <RadioGroup defaultValue="home">
                                            <FormControlLabel value="home" control={<Radio />} label="Home Dashboard" />
                                            <FormControlLabel value="workflows" control={<Radio />} label="Workflows" />
                                            <FormControlLabel value="agents" control={<Radio />} label="Agents" />
                                            <FormControlLabel value="rag" control={<Radio />} label="RAG System" />
                                        </RadioGroup>
                                    </FormControl>
                                </CardContent>
                            </Card>
                        </Grid>

                        <Grid item xs={12} md={6}>
                            <Card>
                                <CardHeader title="User Preferences" />
                                <Divider />
                                <CardContent>
                                    <List>
                                        <ListItem>
                                            <ListItemText
                                                primary="Auto-refresh Dashboards"
                                                secondary="Automatically refresh dashboard data"
                                            />
                                            <ListItemSecondaryAction>
                                                <Switch edge="end" defaultChecked />
                                            </ListItemSecondaryAction>
                                        </ListItem>
                                        <Divider component="li" />
                                        <ListItem>
                                            <ListItemText
                                                primary="Confirm Before Actions"
                                                secondary="Show confirmation dialogs before important actions"
                                            />
                                            <ListItemSecondaryAction>
                                                <Switch edge="end" defaultChecked />
                                            </ListItemSecondaryAction>
                                        </ListItem>
                                        <Divider component="li" />
                                        <ListItem>
                                            <ListItemText
                                                primary="Smooth Transitions"
                                                secondary="Enable animation effects throughout the interface"
                                            />
                                            <ListItemSecondaryAction>
                                                <Switch edge="end" defaultChecked />
                                            </ListItemSecondaryAction>
                                        </ListItem>
                                    </List>

                                    <Typography variant="subtitle2" gutterBottom sx={{ mt: 3 }}>
                                        Date Format
                                    </Typography>
                                    <FormControl component="fieldset">
                                        <RadioGroup defaultValue="system">
                                            <FormControlLabel value="system" control={<Radio />} label="System Default" />
                                            <FormControlLabel value="us" control={<Radio />} label="MM/DD/YYYY" />
                                            <FormControlLabel value="eu" control={<Radio />} label="DD/MM/YYYY" />
                                            <FormControlLabel value="iso" control={<Radio />} label="YYYY-MM-DD" />
                                        </RadioGroup>
                                    </FormControl>
                                </CardContent>
                            </Card>
                        </Grid>
                    </Grid>
                </TabPanel>
            </Paper>

            {/* Notification Snackbar */}
            <Snackbar
                open={snackbar.open}
                autoHideDuration={6000}
                onClose={handleCloseSnackbar}
                anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
            >
                <Alert
                    onClose={handleCloseSnackbar}
                    severity={snackbar.severity}
                    sx={{ width: '100%' }}
                >
                    {snackbar.message}
                </Alert>
            </Snackbar>
        </Box>
    );
};

export default Settings;
