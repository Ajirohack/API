import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
    Box,
    Typography,
    Paper,
    Button,
    AppBar,
    Toolbar,
    IconButton,
    TextField,
    Grid,
    Divider,
    Drawer,
    List,
    ListItem,
    ListItemText,
    ListItemIcon,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    Tabs,
    Tab,
    Alert,
    Snackbar,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
} from '@mui/material';
import {
    Save as SaveIcon,
    PlayArrow as RunIcon,
    ArrowBack as BackIcon,
    Add as AddIcon,
    Delete as DeleteIcon,
    Settings as SettingsIcon,
    Code as CodeIcon,
    DataObject as DataIcon,
    FunctionsOutlined as FunctionIcon,
    Layers as LayersIcon,
    Input as InputIcon,
    Output as OutputIcon,
    Storage as DatabaseIcon,
    TextFields as TextIcon,
    Calculate as CalculateIcon,
    Compare as ConditionIcon,
    LoopOutlined as LoopIcon,
    SmartToy as AgentIcon,
    SettingsInputComponent as ApiIcon,
    Timer as TimerIcon,
} from '@mui/icons-material';

const WorkflowBuilder = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const searchParams = new URLSearchParams(location.search);
    const workflowId = searchParams.get('id');

    const [workflow, setWorkflow] = useState({
        id: workflowId || `new-${Date.now()}`,
        name: '',
        description: '',
        nodes: [],
        edges: [],
    });

    const [selectedNode, setSelectedNode] = useState(null);
    const [configTab, setConfigTab] = useState(0);
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const [codeViewOpen, setCodeViewOpen] = useState(false);
    const [saveDialogOpen, setSaveDialogOpen] = useState(false);
    const [discardDialogOpen, setDiscardDialogOpen] = useState(false);
    const [snackbar, setSnackbar] = useState({
        open: false,
        message: '',
        severity: 'info',
    });

    // Mock function to load existing workflow data
    useEffect(() => {
        const loadWorkflow = async () => {
            if (workflowId) {
                try {
                    // In a real app, this would be fetched from an API
                    // const data = await workflowService.getWorkflowById(workflowId);

                    // Demo data
                    setWorkflow({
                        id: workflowId,
                        name: 'Document Processing Workflow',
                        description: 'Process documents through OCR, extraction, and classification steps',
                        nodes: [
                            { id: 'node1', type: 'trigger', label: 'API Trigger', x: 100, y: 100 },
                            { id: 'node2', type: 'process', label: 'Document Validation', x: 300, y: 100 },
                            { id: 'node3', type: 'condition', label: 'Valid Document?', x: 500, y: 100 },
                            { id: 'node4', type: 'process', label: 'Extract Text', x: 700, y: 50 },
                            { id: 'node5', type: 'process', label: 'Notify Error', x: 700, y: 150 },
                        ],
                        edges: [
                            { id: 'edge1', source: 'node1', target: 'node2' },
                            { id: 'edge2', source: 'node2', target: 'node3' },
                            { id: 'edge3', source: 'node3', target: 'node4', label: 'Yes' },
                            { id: 'edge4', source: 'node3', target: 'node5', label: 'No' },
                        ]
                    });
                } catch (error) {
                    console.error('Error loading workflow:', error);
                    setSnackbar({
                        open: true,
                        message: 'Failed to load workflow',
                        severity: 'error',
                    });
                }
            }
        };

        loadWorkflow();
    }, [workflowId]);

    const handleBack = () => {
        if (isDirty) {
            setDiscardDialogOpen(true);
        } else {
            navigate('/workflows');
        }
    };

    // In a real app, track changes to detect if unsaved
    const isDirty = false;

    const handleSave = async () => {
        try {
            // In a real app, this would save to an API
            // await workflowService.saveWorkflow(workflow);

            setSnackbar({
                open: true,
                message: 'Workflow saved successfully',
                severity: 'success',
            });

            setSaveDialogOpen(false);
        } catch (error) {
            console.error('Error saving workflow:', error);
            setSnackbar({
                open: true,
                message: 'Failed to save workflow',
                severity: 'error',
            });
        }
    };

    const handleRun = async () => {
        try {
            // In a real app, this would call the API to run the workflow
            // await workflowService.executeWorkflow(workflow.id);

            setSnackbar({
                open: true,
                message: 'Workflow execution started',
                severity: 'info',
            });
        } catch (error) {
            console.error('Error running workflow:', error);
            setSnackbar({
                open: true,
                message: 'Failed to run workflow',
                severity: 'error',
            });
        }
    };

    const handleConfirmDiscard = () => {
        setDiscardDialogOpen(false);
        navigate('/workflows');
    };

    const handleCloseSnackbar = () => {
        setSnackbar({
            ...snackbar,
            open: false,
        });
    };

    // Node categories for the sidebar
    const nodeCategories = [
        {
            name: 'Triggers',
            nodes: [
                { type: 'api', label: 'API Trigger', icon: <ApiIcon /> },
                { type: 'schedule', label: 'Schedule', icon: <TimerIcon /> },
                { type: 'event', label: 'Event', icon: <DataIcon /> },
            ]
        },
        {
            name: 'Logic',
            nodes: [
                { type: 'condition', label: 'Condition', icon: <ConditionIcon /> },
                { type: 'switch', label: 'Switch', icon: <LayersIcon /> },
                { type: 'loop', label: 'Loop', icon: <LoopIcon /> },
            ]
        },
        {
            name: 'Actions',
            nodes: [
                { type: 'function', label: 'Function', icon: <FunctionIcon /> },
                { type: 'agent', label: 'AI Agent', icon: <AgentIcon /> },
                { type: 'database', label: 'Database', icon: <DatabaseIcon /> },
                { type: 'text', label: 'Text Processing', icon: <TextIcon /> },
                { type: 'math', label: 'Math Operation', icon: <CalculateIcon /> },
            ]
        },
    ];

    const renderNodeConfiguration = () => {
        if (!selectedNode) {
            return (
                <Box p={2} textAlign="center">
                    <Typography color="textSecondary">
                        Select a node to configure its properties
                    </Typography>
                </Box>
            );
        }

        return (
            <Box p={2}>
                <Typography variant="h6" gutterBottom>
                    {selectedNode.label}
                </Typography>

                <Tabs
                    value={configTab}
                    onChange={(e, newValue) => setConfigTab(newValue)}
                    sx={{ mb: 2 }}
                >
                    <Tab label="Settings" />
                    <Tab label="Input" />
                    <Tab label="Output" />
                </Tabs>

                {configTab === 0 && (
                    <Box>
                        <TextField
                            label="Node Name"
                            fullWidth
                            margin="normal"
                            size="small"
                            value={selectedNode.label}
                        />

                        <TextField
                            label="Description"
                            fullWidth
                            margin="normal"
                            size="small"
                            multiline
                            rows={2}
                        />

                        <FormControl fullWidth margin="normal" size="small">
                            <InputLabel>Node Type</InputLabel>
                            <Select
                                value={selectedNode.type}
                                label="Node Type"
                            >
                                <MenuItem value="trigger">Trigger</MenuItem>
                                <MenuItem value="process">Process</MenuItem>
                                <MenuItem value="condition">Condition</MenuItem>
                                <MenuItem value="action">Action</MenuItem>
                            </Select>
                        </FormControl>
                    </Box>
                )}

                {configTab === 1 && (
                    <Box>
                        <Typography variant="subtitle2" gutterBottom>
                            Input Parameters
                        </Typography>
                        <Alert severity="info" sx={{ mb: 2 }}>
                            Define what input this node requires from previous nodes
                        </Alert>
                        {/* Input parameters configuration would go here */}
                    </Box>
                )}

                {configTab === 2 && (
                    <Box>
                        <Typography variant="subtitle2" gutterBottom>
                            Output Mapping
                        </Typography>
                        <Alert severity="info" sx={{ mb: 2 }}>
                            Define what output this node produces for next nodes
                        </Alert>
                        {/* Output parameters configuration would go here */}
                    </Box>
                )}
            </Box>
        );
    };

    return (
        <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
            {/* Top Toolbar */}
            <AppBar position="static" color="default" elevation={1}>
                <Toolbar>
                    <IconButton edge="start" color="inherit" onClick={handleBack} sx={{ mr: 1 }}>
                        <BackIcon />
                    </IconButton>

                    <Typography variant="h6" sx={{ flexGrow: 0, minWidth: 200 }}>
                        {workflow.name || 'New Workflow'}
                    </Typography>

                    <TextField
                        placeholder="Workflow Name"
                        variant="outlined"
                        size="small"
                        value={workflow.name}
                        onChange={(e) => setWorkflow({ ...workflow, name: e.target.value })}
                        sx={{ flexGrow: 1, mx: 2 }}
                    />

                    <Button
                        startIcon={<CodeIcon />}
                        onClick={() => setCodeViewOpen(true)}
                        sx={{ mr: 1 }}
                    >
                        Code
                    </Button>

                    <Button
                        startIcon={<SettingsIcon />}
                        sx={{ mr: 1 }}
                    >
                        Settings
                    </Button>

                    <Button
                        variant="outlined"
                        startIcon={<RunIcon />}
                        onClick={handleRun}
                        sx={{ mr: 1 }}
                    >
                        Test Run
                    </Button>

                    <Button
                        variant="contained"
                        startIcon={<SaveIcon />}
                        onClick={() => setSaveDialogOpen(true)}
                    >
                        Save
                    </Button>
                </Toolbar>
            </AppBar>

            <Grid container sx={{ flexGrow: 1, overflow: 'hidden' }}>
                {/* Left Sidebar - Node Palette */}
                <Grid item sx={{
                    width: sidebarOpen ? 240 : 0,
                    transition: 'width 0.3s',
                    borderRight: '1px solid rgba(0, 0, 0, 0.12)',
                }}>
                    <Box sx={{ height: '100%', overflow: 'auto' }}>
                        {nodeCategories.map((category) => (
                            <React.Fragment key={category.name}>
                                <Typography variant="subtitle2" sx={{ px: 2, py: 1, fontWeight: 600 }}>
                                    {category.name}
                                </Typography>
                                <List dense>
                                    {category.nodes.map((node) => (
                                        <ListItem
                                            button
                                            key={node.type}
                                            sx={{
                                                cursor: 'grab',
                                                '&:hover': {
                                                    backgroundColor: 'action.hover'
                                                }
                                            }}
                                        >
                                            <ListItemIcon sx={{ minWidth: 36 }}>
                                                {node.icon}
                                            </ListItemIcon>
                                            <ListItemText primary={node.label} />
                                        </ListItem>
                                    ))}
                                </List>
                                <Divider />
                            </React.Fragment>
                        ))}
                    </Box>
                </Grid>

                {/* Center - Canvas */}
                <Grid item xs sx={{ position: 'relative' }}>
                    <Box
                        sx={{
                            bgcolor: 'grey.100',
                            height: '100%',
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            justifyContent: 'center',
                            backgroundImage: 'radial-gradient(#bbb 1px, transparent 1px)',
                            backgroundSize: '20px 20px',
                        }}
                    >
                        <Typography variant="h5" color="textSecondary">
                            Workflow Canvas
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                            Drag and drop nodes from the left sidebar to build your workflow
                        </Typography>
                    </Box>
                </Grid>

                {/* Right Sidebar - Node Configuration */}
                <Grid item sx={{
                    width: 300,
                    borderLeft: '1px solid rgba(0, 0, 0, 0.12)',
                }}>
                    {renderNodeConfiguration()}
                </Grid>
            </Grid>

            {/* Save Dialog */}
            <Dialog open={saveDialogOpen} onClose={() => setSaveDialogOpen(false)}>
                <DialogTitle>Save Workflow</DialogTitle>
                <DialogContent>
                    <TextField
                        label="Workflow Name"
                        fullWidth
                        margin="dense"
                        value={workflow.name}
                        onChange={(e) => setWorkflow({ ...workflow, name: e.target.value })}
                    />
                    <TextField
                        label="Description"
                        fullWidth
                        margin="dense"
                        multiline
                        rows={3}
                        value={workflow.description}
                        onChange={(e) => setWorkflow({ ...workflow, description: e.target.value })}
                    />
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setSaveDialogOpen(false)}>Cancel</Button>
                    <Button
                        variant="contained"
                        color="primary"
                        onClick={handleSave}
                        disabled={!workflow.name}
                    >
                        Save
                    </Button>
                </DialogActions>
            </Dialog>

            {/* Confirm Discard Dialog */}
            <Dialog open={discardDialogOpen} onClose={() => setDiscardDialogOpen(false)}>
                <DialogTitle>Unsaved Changes</DialogTitle>
                <DialogContent>
                    <Typography>
                        You have unsaved changes. Are you sure you want to leave?
                        All unsaved changes will be lost.
                    </Typography>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setDiscardDialogOpen(false)}>Cancel</Button>
                    <Button
                        variant="contained"
                        color="error"
                        onClick={handleConfirmDiscard}
                    >
                        Discard Changes
                    </Button>
                </DialogActions>
            </Dialog>

            {/* Code View Dialog */}
            <Dialog
                open={codeViewOpen}
                onClose={() => setCodeViewOpen(false)}
                fullWidth
                maxWidth="md"
            >
                <DialogTitle>Workflow Code</DialogTitle>
                <DialogContent>
                    <Paper
                        sx={{
                            p: 2,
                            bgcolor: '#f5f5f5',
                            fontFamily: 'monospace',
                            overflowX: 'auto'
                        }}
                    >
                        <pre>
                            {JSON.stringify(workflow, null, 2)}
                        </pre>
                    </Paper>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setCodeViewOpen(false)}>Close</Button>
                </DialogActions>
            </Dialog>

            {/* Notifications */}
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

export default WorkflowBuilder;
