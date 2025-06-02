import React, { useState, useEffect } from 'react';
import {
    Box,
    Typography,
    Paper,
    Button,
    Chip,
    Grid,
    Card,
    CardContent,
    CardActions,
    CardHeader,
    Switch,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    TextField,
    IconButton,
    Alert,
    LinearProgress,
    Divider,
    Avatar,
    Tooltip,
} from '@mui/material';
import {
    Refresh as RefreshIcon,
    Add as AddIcon,
    Settings as SettingsIcon,
    DeleteOutline as DeleteIcon,
    CloudUpload as UploadIcon,
    Info as InfoIcon,
    Article as DocIcon,
} from '@mui/icons-material';

import pluginService from '../services/pluginService';

const Plugins = () => {
    const [plugins, setPlugins] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [openDialog, setOpenDialog] = useState(false);
    const [dialogType, setDialogType] = useState('upload'); // 'upload', 'settings', 'delete'
    const [currentPlugin, setCurrentPlugin] = useState(null);
    const [uploadFile, setUploadFile] = useState(null);

    useEffect(() => {
        fetchPlugins();
    }, []);

    const fetchPlugins = async () => {
        setLoading(true);
        setError(null);

        try {
            const data = await pluginService.getPlugins();
            setPlugins(data);
        } catch (err) {
            console.error('Failed to fetch plugins:', err);
            setError('Failed to load plugins. Please try again.');

            // For demo purposes, load sample data
            setPlugins([
                {
                    id: 'plugin-001',
                    name: 'Data Connector',
                    version: '1.2.0',
                    description: 'Connect to external data sources and import data into the system',
                    author: 'SpaceNew Team',
                    isActive: true,
                    capabilities: ['data-import', 'data-export', 'data-transform'],
                    lastUpdated: '2024-03-15T10:30:00Z',
                    icon: '📊',
                },
                {
                    id: 'plugin-002',
                    name: 'Document Processor',
                    version: '2.1.5',
                    description: 'Process and extract information from various document formats',
                    author: 'Document AI Inc',
                    isActive: true,
                    capabilities: ['document-parsing', 'text-extraction', 'metadata-analysis'],
                    lastUpdated: '2024-04-02T14:45:00Z',
                    icon: '📄',
                },
                {
                    id: 'plugin-003',
                    name: 'Email Integration',
                    version: '1.0.1',
                    description: 'Integrate with email services to send notifications and process incoming emails',
                    author: 'Communication Systems LLC',
                    isActive: false,
                    capabilities: ['email-sending', 'email-receiving', 'template-rendering'],
                    lastUpdated: '2024-02-28T09:15:00Z',
                    icon: '📧',
                },
                {
                    id: 'plugin-004',
                    name: 'Advanced Analytics',
                    version: '3.0.0',
                    description: 'Perform advanced analytics and generate insights from system data',
                    author: 'Data Science Group',
                    isActive: true,
                    capabilities: ['data-analysis', 'visualization', 'reporting', 'prediction'],
                    lastUpdated: '2024-04-10T16:20:00Z',
                    icon: '📈',
                }
            ]);
        } finally {
            setLoading(false);
        }
    };

    const handleToggleActive = async (plugin, newStatus) => {
        try {
            // In a real app, this would call the API
            // await pluginService.updatePluginStatus(plugin.id, newStatus);

            // Update local state
            setPlugins(plugins.map(p =>
                p.id === plugin.id ? { ...p, isActive: newStatus } : p
            ));
        } catch (err) {
            console.error('Failed to update plugin status:', err);
            setError('Failed to update plugin status. Please try again.');
        }
    };

    const handleOpenDialog = (type, plugin = null) => {
        setDialogType(type);
        setCurrentPlugin(plugin);
        setOpenDialog(true);
    };

    const handleCloseDialog = () => {
        setOpenDialog(false);
        setCurrentPlugin(null);
        setUploadFile(null);
    };

    const handleFileChange = (event) => {
        setUploadFile(event.target.files[0]);
    };

    const handleUploadPlugin = async () => {
        if (!uploadFile) {
            return;
        }

        try {
            // In a real app, this would upload to the backend
            // await pluginService.uploadPlugin(uploadFile);

            // Simulate success for demo
            setTimeout(() => {
                handleCloseDialog();
                fetchPlugins();
            }, 1500);
        } catch (err) {
            console.error('Failed to upload plugin:', err);
            setError('Failed to upload plugin. Please try again.');
        }
    };

    const handleDeletePlugin = async () => {
        if (!currentPlugin) {
            return;
        }

        try {
            // In a real app, call the API
            // await pluginService.deletePlugin(currentPlugin.id);

            // Update local state
            setPlugins(plugins.filter(p => p.id !== currentPlugin.id));
            handleCloseDialog();
        } catch (err) {
            console.error('Failed to delete plugin:', err);
            setError('Failed to delete plugin. Please try again.');
        }
    };

    const renderDialogContent = () => {
        switch (dialogType) {
            case 'upload':
                return (
                    <>
                        <DialogTitle>Upload New Plugin</DialogTitle>
                        <DialogContent>
                            <Box my={2}>
                                <Button
                                    variant="outlined"
                                    component="label"
                                    startIcon={<UploadIcon />}
                                    fullWidth
                                    sx={{ height: 100, border: '2px dashed #ccc' }}
                                >
                                    {uploadFile ? uploadFile.name : 'Select Plugin Package (.zip)'}
                                    <input
                                        type="file"
                                        accept=".zip"
                                        hidden
                                        onChange={handleFileChange}
                                    />
                                </Button>
                            </Box>
                            <Typography variant="caption" color="text.secondary">
                                Upload a ZIP file containing the plugin manifest and required files.
                                The plugin should follow the SpaceNew plugin format.
                            </Typography>
                        </DialogContent>
                        <DialogActions>
                            <Button onClick={handleCloseDialog} color="inherit">Cancel</Button>
                            <Button
                                onClick={handleUploadPlugin}
                                color="primary"
                                variant="contained"
                                disabled={!uploadFile}
                            >
                                Upload
                            </Button>
                        </DialogActions>
                    </>
                );

            case 'delete':
                return (
                    <>
                        <DialogTitle>Confirm Delete</DialogTitle>
                        <DialogContent>
                            <Typography variant="body1">
                                Are you sure you want to delete the plugin "{currentPlugin?.name}"?
                            </Typography>
                            <Alert severity="warning" sx={{ mt: 2 }}>
                                This action cannot be undone. All data associated with this plugin will be permanently removed.
                            </Alert>
                        </DialogContent>
                        <DialogActions>
                            <Button onClick={handleCloseDialog} color="inherit">Cancel</Button>
                            <Button
                                onClick={handleDeletePlugin}
                                color="error"
                                variant="contained"
                            >
                                Delete
                            </Button>
                        </DialogActions>
                    </>
                );

            case 'settings':
                return (
                    <>
                        <DialogTitle>Plugin Settings: {currentPlugin?.name}</DialogTitle>
                        <DialogContent>
                            <TextField
                                label="Plugin Name"
                                fullWidth
                                margin="normal"
                                defaultValue={currentPlugin?.name}
                            />
                            <TextField
                                label="Description"
                                fullWidth
                                margin="normal"
                                multiline
                                rows={3}
                                defaultValue={currentPlugin?.description}
                            />
                            <Box mt={2}>
                                <Typography variant="subtitle2" gutterBottom>
                                    Plugin Status
                                </Typography>
                                <Grid container alignItems="center">
                                    <Grid item>
                                        <Switch
                                            checked={currentPlugin?.isActive || false}
                                            onChange={(e) => handleToggleActive(currentPlugin, e.target.checked)}
                                        />
                                    </Grid>
                                    <Grid item>
                                        <Typography variant="body2">
                                            {currentPlugin?.isActive ? 'Active' : 'Inactive'}
                                        </Typography>
                                    </Grid>
                                </Grid>
                            </Box>
                        </DialogContent>
                        <DialogActions>
                            <Button onClick={handleCloseDialog} color="inherit">Cancel</Button>
                            <Button
                                onClick={handleCloseDialog}
                                color="primary"
                                variant="contained"
                            >
                                Save Changes
                            </Button>
                        </DialogActions>
                    </>
                );

            default:
                return null;
        }
    };

    return (
        <Box>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Typography variant="h4" component="h1">
                    Plugins
                </Typography>
                <Box>
                    <Button
                        variant="contained"
                        color="primary"
                        startIcon={<AddIcon />}
                        onClick={() => handleOpenDialog('upload')}
                        sx={{ mr: 1 }}
                    >
                        Add Plugin
                    </Button>
                    <IconButton color="inherit" onClick={fetchPlugins}>
                        <RefreshIcon />
                    </IconButton>
                </Box>
            </Box>

            {error && (
                <Alert severity="error" sx={{ mb: 3 }}>
                    {error}
                </Alert>
            )}

            {loading ? (
                <LinearProgress sx={{ mb: 4 }} />
            ) : (
                <Grid container spacing={3}>
                    {plugins.map((plugin) => (
                        <Grid item xs={12} md={6} key={plugin.id}>
                            <Card>
                                <CardHeader
                                    avatar={
                                        <Avatar sx={{ bgcolor: plugin.isActive ? 'primary.main' : 'grey.400' }}>
                                            {plugin.icon || plugin.name.charAt(0)}
                                        </Avatar>
                                    }
                                    action={
                                        <Box display="flex" alignItems="center">
                                            <Tooltip title={plugin.isActive ? 'Active' : 'Inactive'}>
                                                <Switch
                                                    checked={plugin.isActive}
                                                    onChange={(e) => handleToggleActive(plugin, e.target.checked)}
                                                    color="primary"
                                                    size="small"
                                                />
                                            </Tooltip>
                                            <IconButton size="small" onClick={() => handleOpenDialog('settings', plugin)}>
                                                <SettingsIcon fontSize="small" />
                                            </IconButton>
                                        </Box>
                                    }
                                    title={
                                        <Typography variant="h6" component="h2">
                                            {plugin.name}
                                            <Typography component="span" variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                                                v{plugin.version}
                                            </Typography>
                                        </Typography>
                                    }
                                    subheader={`By ${plugin.author}`}
                                />
                                <Divider />
                                <CardContent>
                                    <Typography variant="body2" color="text.secondary" mb={2}>
                                        {plugin.description}
                                    </Typography>
                                    <Box display="flex" flexWrap="wrap" gap={1}>
                                        {plugin.capabilities.map((cap, index) => (
                                            <Chip
                                                key={index}
                                                label={cap}
                                                size="small"
                                                color={plugin.isActive ? "primary" : "default"}
                                                variant="outlined"
                                            />
                                        ))}
                                    </Box>
                                </CardContent>
                                <Divider />
                                <CardActions sx={{ justifyContent: 'space-between' }}>
                                    <Box>
                                        <Tooltip title="Plugin documentation">
                                            <IconButton size="small">
                                                <DocIcon fontSize="small" />
                                            </IconButton>
                                        </Tooltip>
                                        <Tooltip title="Plugin info">
                                            <IconButton size="small">
                                                <InfoIcon fontSize="small" />
                                            </IconButton>
                                        </Tooltip>
                                    </Box>
                                    <Box>
                                        <Typography variant="caption" color="text.secondary">
                                            Updated: {new Date(plugin.lastUpdated).toLocaleDateString()}
                                        </Typography>
                                        <IconButton
                                            size="small"
                                            color="error"
                                            sx={{ ml: 1 }}
                                            onClick={() => handleOpenDialog('delete', plugin)}
                                        >
                                            <DeleteIcon fontSize="small" />
                                        </IconButton>
                                    </Box>
                                </CardActions>
                            </Card>
                        </Grid>
                    ))}
                </Grid>
            )}

            {/* Dialog for plugin operations */}
            <Dialog
                open={openDialog}
                onClose={handleCloseDialog}
                maxWidth="sm"
                fullWidth
            >
                {renderDialogContent()}
            </Dialog>
        </Box>
    );
};

export default Plugins;
