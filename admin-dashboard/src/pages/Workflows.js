import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
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
    IconButton,
    Tooltip,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    TablePagination,
    LinearProgress,
    Alert,
    TextField,
    InputAdornment,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
} from '@mui/material';
import {
    Add as AddIcon,
    Search as SearchIcon,
    Refresh as RefreshIcon,
    Edit as EditIcon,
    PlayArrow as RunIcon,
    Pause as PauseIcon,
    Delete as DeleteIcon,
    FileCopy as CloneIcon,
    History as HistoryIcon,
} from '@mui/icons-material';

import workflowService from '../services/workflowService';

// Status component with appropriate colors
const StatusChip = ({ status }) => {
    let color, icon;

    switch (status.toLowerCase()) {
        case 'active':
            color = 'success';
            break;
        case 'draft':
            color = 'default';
            break;
        case 'paused':
            color = 'warning';
            break;
        case 'error':
            color = 'error';
            break;
        default:
            color = 'default';
    }

    return <Chip size="small" label={status} color={color} />;
};

const Workflows = () => {
    const navigate = useNavigate();
    const [workflows, setWorkflows] = useState([]);
    const [filteredWorkflows, setFilteredWorkflows] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [search, setSearch] = useState('');
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(10);
    const [selectedWorkflow, setSelectedWorkflow] = useState(null);
    const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);

    useEffect(() => {
        fetchWorkflows();
    }, []);

    useEffect(() => {
        if (search.trim() === '') {
            setFilteredWorkflows(workflows);
        } else {
            const filtered = workflows.filter(workflow =>
                workflow.name.toLowerCase().includes(search.toLowerCase()) ||
                workflow.description.toLowerCase().includes(search.toLowerCase()) ||
                workflow.tags.some(tag => tag.toLowerCase().includes(search.toLowerCase()))
            );
            setFilteredWorkflows(filtered);
        }
    }, [search, workflows]);

    const fetchWorkflows = async () => {
        setLoading(true);
        setError(null);

        try {
            // In a real app, this would fetch from the API
            // const data = await workflowService.getWorkflows();

            // Sample data for demo
            const sampleWorkflows = [
                {
                    id: 'wf-001',
                    name: 'Document Processing Pipeline',
                    description: 'Process documents through OCR, extraction, and classification steps',
                    status: 'Active',
                    created: '2024-04-01T10:30:00Z',
                    lastRun: '2024-04-15T09:45:00Z',
                    executionCount: 128,
                    averageDuration: 45.2,
                    successRate: 97.8,
                    tags: ['document', 'processing', 'extraction'],
                    triggers: ['api', 'scheduled'],
                    owner: 'admin'
                },
                {
                    id: 'wf-002',
                    name: 'Customer Onboarding',
                    description: 'Automated customer onboarding workflow with verification steps',
                    status: 'Active',
                    created: '2024-03-12T14:20:00Z',
                    lastRun: '2024-04-14T16:32:00Z',
                    executionCount: 76,
                    averageDuration: 120.5,
                    successRate: 94.2,
                    tags: ['customer', 'onboarding', 'verification'],
                    triggers: ['api', 'event'],
                    owner: 'admin'
                },
                {
                    id: 'wf-003',
                    name: 'Data Synchronization',
                    description: 'Sync data between internal systems and external services',
                    status: 'Paused',
                    created: '2024-02-28T09:15:00Z',
                    lastRun: '2024-04-10T03:00:00Z',
                    executionCount: 315,
                    averageDuration: 18.7,
                    successRate: 99.1,
                    tags: ['data', 'sync', 'integration'],
                    triggers: ['scheduled', 'manual'],
                    owner: 'system'
                },
                {
                    id: 'wf-004',
                    name: 'Alert Notification',
                    description: 'Send alerts based on system events and thresholds',
                    status: 'Error',
                    created: '2024-03-05T11:45:00Z',
                    lastRun: '2024-04-14T22:17:00Z',
                    executionCount: 52,
                    averageDuration: 5.3,
                    successRate: 88.5,
                    tags: ['alerts', 'notifications'],
                    triggers: ['event'],
                    owner: 'admin'
                },
                {
                    id: 'wf-005',
                    name: 'Report Generation',
                    description: 'Generate and distribute automated reports on schedule',
                    status: 'Active',
                    created: '2024-01-15T08:30:00Z',
                    lastRun: '2024-04-15T01:00:00Z',
                    executionCount: 90,
                    averageDuration: 67.8,
                    successRate: 100.0,
                    tags: ['reports', 'analytics', 'scheduled'],
                    triggers: ['scheduled'],
                    owner: 'admin'
                },
                {
                    id: 'wf-006',
                    name: 'User Activity Analysis',
                    description: 'Analyze user behavior patterns and generate insights',
                    status: 'Draft',
                    created: '2024-04-05T16:20:00Z',
                    lastRun: null,
                    executionCount: 0,
                    averageDuration: null,
                    successRate: null,
                    tags: ['analytics', 'user', 'behavior'],
                    triggers: [],
                    owner: 'admin'
                }
            ];

            setWorkflows(sampleWorkflows);
            setFilteredWorkflows(sampleWorkflows);
        } catch (err) {
            console.error('Failed to fetch workflows:', err);
            setError('Failed to load workflows. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleChangePage = (event, newPage) => {
        setPage(newPage);
    };

    const handleChangeRowsPerPage = (event) => {
        setRowsPerPage(parseInt(event.target.value, 10));
        setPage(0);
    };

    const handleSearchChange = (event) => {
        setSearch(event.target.value);
        setPage(0);
    };

    const handleCreateWorkflow = () => {
        navigate('/workflows/builder');
    };

    const handleEditWorkflow = (workflowId) => {
        navigate(`/workflows/builder?id=${workflowId}`);
    };

    const handleRunWorkflow = async (workflowId) => {
        try {
            // In a real app, this would call the API
            // await workflowService.executeWorkflow(workflowId);

            // For demo, just log
            console.log(`Running workflow: ${workflowId}`);
        } catch (err) {
            console.error('Failed to run workflow:', err);
            setError('Failed to execute workflow. Please try again.');
        }
    };

    const handleDeleteClick = (workflow) => {
        setSelectedWorkflow(workflow);
        setDeleteDialogOpen(true);
    };

    const handleDeleteConfirm = async () => {
        if (!selectedWorkflow) return;

        try {
            // In a real app, this would call the API
            // await workflowService.deleteWorkflow(selectedWorkflow.id);

            // Update state
            const updatedWorkflows = workflows.filter(w => w.id !== selectedWorkflow.id);
            setWorkflows(updatedWorkflows);
            setFilteredWorkflows(updatedWorkflows);
        } catch (err) {
            console.error('Failed to delete workflow:', err);
            setError('Failed to delete workflow. Please try again.');
        } finally {
            setDeleteDialogOpen(false);
            setSelectedWorkflow(null);
        }
    };

    const handleCloneWorkflow = async (workflowId) => {
        try {
            // In a real app, this would call the API
            // await workflowService.cloneWorkflow(workflowId);

            // For demo, just log
            console.log(`Cloning workflow: ${workflowId}`);
        } catch (err) {
            console.error('Failed to clone workflow:', err);
            setError('Failed to clone workflow. Please try again.');
        }
    };

    return (
        <Box>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Typography variant="h4" component="h1">
                    Workflows
                </Typography>
                <Box display="flex">
                    <Button
                        variant="contained"
                        color="primary"
                        startIcon={<AddIcon />}
                        onClick={handleCreateWorkflow}
                        sx={{ mr: 1 }}
                    >
                        Create Workflow
                    </Button>
                    <IconButton color="inherit" onClick={fetchWorkflows}>
                        <RefreshIcon />
                    </IconButton>
                </Box>
            </Box>

            {error && (
                <Alert severity="error" sx={{ mb: 3 }}>
                    {error}
                </Alert>
            )}

            <Paper sx={{ width: '100%', mb: 2 }}>
                <Box sx={{ p: 2 }}>
                    <TextField
                        fullWidth
                        variant="outlined"
                        placeholder="Search workflows..."
                        value={search}
                        onChange={handleSearchChange}
                        InputProps={{
                            startAdornment: (
                                <InputAdornment position="start">
                                    <SearchIcon />
                                </InputAdornment>
                            ),
                        }}
                        size="small"
                    />
                </Box>

                {loading ? (
                    <LinearProgress />
                ) : (
                    <>
                        <TableContainer>
                            <Table>
                                <TableHead>
                                    <TableRow>
                                        <TableCell>Name</TableCell>
                                        <TableCell>Status</TableCell>
                                        <TableCell>Last Run</TableCell>
                                        <TableCell>Success Rate</TableCell>
                                        <TableCell>Triggers</TableCell>
                                        <TableCell>Tags</TableCell>
                                        <TableCell align="center">Actions</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {filteredWorkflows
                                        .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                                        .map((workflow) => (
                                            <TableRow key={workflow.id} hover>
                                                <TableCell>
                                                    <Typography variant="subtitle2">
                                                        {workflow.name}
                                                    </Typography>
                                                    <Typography variant="caption" color="text.secondary">
                                                        {workflow.description}
                                                    </Typography>
                                                </TableCell>
                                                <TableCell>
                                                    <StatusChip status={workflow.status} />
                                                </TableCell>
                                                <TableCell>
                                                    {workflow.lastRun
                                                        ? new Date(workflow.lastRun).toLocaleString()
                                                        : 'Never run'}
                                                </TableCell>
                                                <TableCell>
                                                    {workflow.successRate !== null
                                                        ? `${workflow.successRate}%`
                                                        : 'N/A'}
                                                </TableCell>
                                                <TableCell>
                                                    <Box display="flex" flexWrap="wrap" gap={0.5}>
                                                        {workflow.triggers.map((trigger, i) => (
                                                            <Chip
                                                                key={i}
                                                                label={trigger}
                                                                size="small"
                                                                variant="outlined"
                                                            />
                                                        ))}
                                                    </Box>
                                                </TableCell>
                                                <TableCell>
                                                    <Box display="flex" flexWrap="wrap" gap={0.5}>
                                                        {workflow.tags.map((tag, i) => (
                                                            <Chip
                                                                key={i}
                                                                label={tag}
                                                                size="small"
                                                            />
                                                        ))}
                                                    </Box>
                                                </TableCell>
                                                <TableCell align="center">
                                                    <Box display="flex" justifyContent="center">
                                                        <Tooltip title="Run workflow">
                                                            <IconButton
                                                                size="small"
                                                                color="primary"
                                                                onClick={() => handleRunWorkflow(workflow.id)}
                                                                disabled={workflow.status === 'Draft'}
                                                            >
                                                                <RunIcon fontSize="small" />
                                                            </IconButton>
                                                        </Tooltip>

                                                        <Tooltip title="Edit">
                                                            <IconButton
                                                                size="small"
                                                                onClick={() => handleEditWorkflow(workflow.id)}
                                                            >
                                                                <EditIcon fontSize="small" />
                                                            </IconButton>
                                                        </Tooltip>

                                                        <Tooltip title="Clone">
                                                            <IconButton
                                                                size="small"
                                                                onClick={() => handleCloneWorkflow(workflow.id)}
                                                            >
                                                                <CloneIcon fontSize="small" />
                                                            </IconButton>
                                                        </Tooltip>

                                                        <Tooltip title="Execution history">
                                                            <IconButton
                                                                size="small"
                                                            >
                                                                <HistoryIcon fontSize="small" />
                                                            </IconButton>
                                                        </Tooltip>

                                                        <Tooltip title="Delete">
                                                            <IconButton
                                                                size="small"
                                                                color="error"
                                                                onClick={() => handleDeleteClick(workflow)}
                                                            >
                                                                <DeleteIcon fontSize="small" />
                                                            </IconButton>
                                                        </Tooltip>
                                                    </Box>
                                                </TableCell>
                                            </TableRow>
                                        ))}
                                </TableBody>
                            </Table>
                        </TableContainer>
                        <TablePagination
                            rowsPerPageOptions={[5, 10, 25]}
                            component="div"
                            count={filteredWorkflows.length}
                            rowsPerPage={rowsPerPage}
                            page={page}
                            onPageChange={handleChangePage}
                            onRowsPerPageChange={handleChangeRowsPerPage}
                        />
                    </>
                )}
            </Paper>

            {/* Delete Confirmation Dialog */}
            <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
                <DialogTitle>Confirm Deletion</DialogTitle>
                <DialogContent>
                    <Typography>
                        Are you sure you want to delete the workflow "{selectedWorkflow?.name}"?
                        This action cannot be undone.
                    </Typography>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
                    <Button onClick={handleDeleteConfirm} variant="contained" color="error">
                        Delete
                    </Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
};

export default Workflows;
