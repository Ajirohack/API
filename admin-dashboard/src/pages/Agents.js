import React, { useState, useEffect } from 'react';
import {
    Box,
    Typography,
    Paper,
    Button,
    Grid,
    Card,
    CardContent,
    CardHeader,
    CardActions,
    Avatar,
    Switch,
    Chip,
    TextField,
    InputAdornment,
    IconButton,
    Divider,
    Dialog,
    DialogContent,
    DialogTitle,
    DialogActions,
    LinearProgress,
    Alert,
    Tabs,
    Tab,
    List,
    ListItem,
    ListItemText,
    ListItemIcon,
    Tooltip,
} from '@mui/material';
import {
    Add as AddIcon,
    Search as SearchIcon,
    Refresh as RefreshIcon,
    Edit as EditIcon,
    Delete as DeleteIcon,
    ContentCopy as CloneIcon,
    Assessment as StatsIcon,
    Settings as SettingsIcon,
    SmartToy as AgentIcon,
    Psychology as BrainIcon,
    Tune as TuneIcon,
    Code as CodeIcon,
    Chat as ChatIcon,
} from '@mui/icons-material';

import agentService from '../services/agentService';

// Agent Type Avatar component
const AgentAvatar = ({ type }) => {
    const getAvatarProps = () => {
        switch (type?.toLowerCase()) {
            case 'chat':
                return {
                    bgcolor: '#4caf50',
                    children: <ChatIcon />,
                };
            case 'reasoning':
                return {
                    bgcolor: '#2196f3',
                    children: <BrainIcon />,
                };
            case 'task':
                return {
                    bgcolor: '#ff9800',
                    children: <TuneIcon />,
                };
            case 'code':
                return {
                    bgcolor: '#9c27b0',
                    children: <CodeIcon />,
                };
            default:
                return {
                    bgcolor: '#607d8b',
                    children: <AgentIcon />,
                };
        }
    };

    return <Avatar {...getAvatarProps()} />;
};

const Agents = () => {
    const [agents, setAgents] = useState([]);
    const [filteredAgents, setFilteredAgents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [search, setSearch] = useState('');
    const [tabValue, setTabValue] = useState(0);
    const [createDialogOpen, setCreateDialogOpen] = useState(false);
    const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
    const [selectedAgent, setSelectedAgent] = useState(null);

    // Fetch agents on component mount
    useEffect(() => {
        fetchAgents();
    }, []);

    // Filter agents when search changes
    useEffect(() => {
        if (search.trim() === '') {
            setFilteredAgents(agents);
        } else {
            const filtered = agents.filter(agent =>
                agent.name.toLowerCase().includes(search.toLowerCase()) ||
                agent.description.toLowerCase().includes(search.toLowerCase())
            );
            setFilteredAgents(filtered);
        }
    }, [search, agents]);

    // Filter agents when tab changes
    useEffect(() => {
        if (tabValue === 0) {
            setFilteredAgents(agents);
        } else {
            const filtered = agents.filter(agent => {
                switch (tabValue) {
                    case 1: return agent.isActive;
                    case 2: return !agent.isActive;
                    default: return true;
                }
            });
            setFilteredAgents(filtered);
        }
    }, [tabValue, agents]);

    const fetchAgents = async () => {
        setLoading(true);
        setError(null);

        try {
            // In a real app, this would be an API call
            // const data = await agentService.getAgents();

            // Sample data for demo
            const sampleAgents = [
                {
                    id: 'agent-001',
                    name: 'General Assistant',
                    description: 'General purpose conversational AI assistant for answering questions and helping users',
                    agentType: 'chat',
                    modelName: 'gpt-4',
                    provider: 'OpenAI',
                    isActive: true,
                    capabilities: ['conversation', 'information-retrieval', 'general-knowledge'],
                    lastActive: '2024-04-15T13:20:00Z',
                    interactions: 1503,
                    avgResponseTime: 0.8,
                    createdAt: '2024-01-20T09:00:00Z',
                },
                {
                    id: 'agent-002',
                    name: 'Data Analyst',
                    description: 'Specialized agent for data analysis and visualization tasks',
                    agentType: 'reasoning',
                    modelName: 'claude-3-opus',
                    provider: 'Anthropic',
                    isActive: true,
                    capabilities: ['data-analysis', 'statistics', 'visualization'],
                    lastActive: '2024-04-14T18:45:00Z',
                    interactions: 782,
                    avgResponseTime: 1.2,
                    createdAt: '2024-02-10T14:30:00Z',
                },
                {
                    id: 'agent-003',
                    name: 'Code Generator',
                    description: 'Generates and explains code in various programming languages',
                    agentType: 'code',
                    modelName: 'gpt-4',
                    provider: 'OpenAI',
                    isActive: false,
                    capabilities: ['code-generation', 'code-explanation', 'debugging'],
                    lastActive: '2024-04-05T10:15:00Z',
                    interactions: 421,
                    avgResponseTime: 2.1,
                    createdAt: '2024-03-01T11:00:00Z',
                },
                {
                    id: 'agent-004',
                    name: 'Document Processor',
                    description: 'Extracts information from documents and answers questions about them',
                    agentType: 'task',
                    modelName: 'mistral-large',
                    provider: 'Mistral AI',
                    isActive: true,
                    capabilities: ['document-analysis', 'information-extraction', 'summarization'],
                    lastActive: '2024-04-15T09:30:00Z',
                    interactions: 953,
                    avgResponseTime: 1.5,
                    createdAt: '2024-02-15T08:45:00Z',
                }
            ];

            setAgents(sampleAgents);
            setFilteredAgents(sampleAgents);
        } catch (err) {
            console.error('Failed to fetch agents:', err);
            setError('Failed to load agents. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleToggleActive = async (agent, newStatus) => {
        try {
            // In a real app, this would call the API
            // await agentService.updateAgentStatus(agent.id, newStatus);

            // Update local state
            setAgents(agents.map(a =>
                a.id === agent.id ? { ...a, isActive: newStatus } : a
            ));
        } catch (err) {
            console.error('Failed to update agent status:', err);
            setError('Failed to update agent status. Please try again.');
        }
    };

    const handleSearchChange = (e) => {
        setSearch(e.target.value);
    };

    const handleTabChange = (event, newValue) => {
        setTabValue(newValue);
    };

    const handleDeleteClick = (agent) => {
        setSelectedAgent(agent);
        setDeleteDialogOpen(true);
    };

    const handleDeleteConfirm = async () => {
        if (!selectedAgent) return;

        try {
            // In a real app, this would call the API
            // await agentService.deleteAgent(selectedAgent.id);

            // Update state
            setAgents(agents.filter(agent => agent.id !== selectedAgent.id));
            setDeleteDialogOpen(false);
            setSelectedAgent(null);
        } catch (err) {
            console.error('Failed to delete agent:', err);
            setError('Failed to delete agent. Please try again.');
        }
    };

    const handleCreateAgent = () => {
        setCreateDialogOpen(true);
    };

    return (
        <Box>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Typography variant="h4" component="h1">
                    AI Agents
                </Typography>
                <Box>
                    <Button
                        variant="contained"
                        color="primary"
                        startIcon={<AddIcon />}
                        onClick={handleCreateAgent}
                        sx={{ mr: 1 }}
                    >
                        Create Agent
                    </Button>
                    <IconButton color="inherit" onClick={fetchAgents}>
                        <RefreshIcon />
                    </IconButton>
                </Box>
            </Box>

            {error && (
                <Alert severity="error" sx={{ mb: 3 }}>
                    {error}
                </Alert>
            )}

            <Paper sx={{ mb: 3 }}>
                <Box p={2} display="flex" alignItems="center">
                    <TextField
                        placeholder="Search agents..."
                        variant="outlined"
                        size="small"
                        value={search}
                        onChange={handleSearchChange}
                        sx={{ mr: 2, flexGrow: 1 }}
                        InputProps={{
                            startAdornment: (
                                <InputAdornment position="start">
                                    <SearchIcon />
                                </InputAdornment>
                            ),
                        }}
                    />
                </Box>

                <Divider />

                <Tabs
                    value={tabValue}
                    onChange={handleTabChange}
                    indicatorColor="primary"
                    textColor="primary"
                    sx={{ px: 2 }}
                >
                    <Tab label="All Agents" />
                    <Tab label="Active" />
                    <Tab label="Inactive" />
                </Tabs>

                <Divider />
            </Paper>

            {loading ? (
                <LinearProgress sx={{ mb: 4 }} />
            ) : (
                <Grid container spacing={3}>
                    {filteredAgents.length === 0 ? (
                        <Grid item xs={12}>
                            <Paper sx={{ p: 4, textAlign: 'center' }}>
                                <Typography variant="h6" color="textSecondary">
                                    No agents found
                                </Typography>
                                <Typography variant="body2" color="textSecondary">
                                    {search ? 'Try a different search term' : 'Add your first AI agent'}
                                </Typography>
                            </Paper>
                        </Grid>
                    ) : (
                        filteredAgents.map(agent => (
                            <Grid item xs={12} md={6} key={agent.id}>
                                <Card>
                                    <CardHeader
                                        avatar={<AgentAvatar type={agent.agentType} />}
                                        title={
                                            <Box display="flex" alignItems="center" justifyContent="space-between">
                                                <Typography variant="h6">
                                                    {agent.name}
                                                </Typography>
                                                <Switch
                                                    checked={agent.isActive}
                                                    onChange={(e) => handleToggleActive(agent, e.target.checked)}
                                                    size="small"
                                                />
                                            </Box>
                                        }
                                        subheader={
                                            <Box display="flex" alignItems="center" gap={1}>
                                                <Chip size="small" label={agent.modelName} />
                                                <Typography variant="caption" color="text.secondary">
                                                    {agent.provider}
                                                </Typography>
                                            </Box>
                                        }
                                    />

                                    <Divider />

                                    <CardContent>
                                        <Typography variant="body2" color="text.secondary" paragraph>
                                            {agent.description}
                                        </Typography>

                                        <Box display="flex" flexWrap="wrap" gap={0.5} mb={2}>
                                            {agent.capabilities.map((cap, index) => (
                                                <Chip
                                                    key={index}
                                                    label={cap}
                                                    size="small"
                                                    variant="outlined"
                                                />
                                            ))}
                                        </Box>

                                        <Grid container spacing={2}>
                                            <Grid item xs={4}>
                                                <Typography variant="caption" color="text.secondary" display="block">
                                                    Interactions
                                                </Typography>
                                                <Typography variant="body2" fontWeight="medium">
                                                    {agent.interactions.toLocaleString()}
                                                </Typography>
                                            </Grid>
                                            <Grid item xs={4}>
                                                <Typography variant="caption" color="text.secondary" display="block">
                                                    Avg Response
                                                </Typography>
                                                <Typography variant="body2" fontWeight="medium">
                                                    {agent.avgResponseTime}s
                                                </Typography>
                                            </Grid>
                                            <Grid item xs={4}>
                                                <Typography variant="caption" color="text.secondary" display="block">
                                                    Last Active
                                                </Typography>
                                                <Typography variant="body2" fontWeight="medium">
                                                    {new Date(agent.lastActive).toLocaleDateString()}
                                                </Typography>
                                            </Grid>
                                        </Grid>
                                    </CardContent>

                                    <Divider />

                                    <CardActions sx={{ justifyContent: 'flex-end' }}>
                                        <Tooltip title="Agent settings">
                                            <IconButton size="small">
                                                <SettingsIcon fontSize="small" />
                                            </IconButton>
                                        </Tooltip>
                                        <Tooltip title="Analytics">
                                            <IconButton size="small">
                                                <StatsIcon fontSize="small" />
                                            </IconButton>
                                        </Tooltip>
                                        <Tooltip title="Clone agent">
                                            <IconButton size="small">
                                                <CloneIcon fontSize="small" />
                                            </IconButton>
                                        </Tooltip>
                                        <Tooltip title="Edit agent">
                                            <IconButton size="small">
                                                <EditIcon fontSize="small" />
                                            </IconButton>
                                        </Tooltip>
                                        <Tooltip title="Delete agent">
                                            <IconButton
                                                size="small"
                                                color="error"
                                                onClick={() => handleDeleteClick(agent)}
                                            >
                                                <DeleteIcon fontSize="small" />
                                            </IconButton>
                                        </Tooltip>
                                    </CardActions>
                                </Card>
                            </Grid>
                        ))
                    )}
                </Grid>
            )}

            {/* Create Agent Dialog */}
            <Dialog
                open={createDialogOpen}
                onClose={() => setCreateDialogOpen(false)}
                maxWidth="md"
                fullWidth
            >
                <DialogTitle>Create New Agent</DialogTitle>
                <DialogContent>
                    <Typography variant="body2" color="text.secondary" paragraph sx={{ mt: 1 }}>
                        Create a new AI agent by configuring its basic settings, capabilities, and model.
                    </Typography>

                    <Grid container spacing={2}>
                        <Grid item xs={12} sm={6}>
                            <TextField
                                label="Agent Name"
                                fullWidth
                                margin="normal"
                            />
                            <TextField
                                label="Description"
                                fullWidth
                                margin="normal"
                                multiline
                                rows={3}
                            />

                            <Box mt={2}>
                                <Typography variant="subtitle2" gutterBottom>
                                    Agent Type
                                </Typography>
                                <Grid container spacing={1}>
                                    {['chat', 'reasoning', 'task', 'code'].map((type) => (
                                        <Grid item xs={6} key={type}>
                                            <Card variant="outlined" sx={{ cursor: 'pointer' }}>
                                                <CardContent sx={{
                                                    display: 'flex',
                                                    alignItems: 'center',
                                                    p: 1,
                                                    '&:last-child': { pb: 1 }
                                                }}>
                                                    <AgentAvatar type={type} />
                                                    <Typography sx={{ ml: 1, textTransform: 'capitalize' }}>
                                                        {type}
                                                    </Typography>
                                                </CardContent>
                                            </Card>
                                        </Grid>
                                    ))}
                                </Grid>
                            </Box>
                        </Grid>

                        <Grid item xs={12} sm={6}>
                            <Typography variant="subtitle2" gutterBottom>
                                Model Configuration
                            </Typography>

                            <TextField
                                select
                                fullWidth
                                label="Provider"
                                margin="normal"
                                defaultValue="openai"
                                SelectProps={{ native: true }}
                            >
                                <option value="openai">OpenAI</option>
                                <option value="anthropic">Anthropic</option>
                                <option value="mistral">Mistral AI</option>
                                <option value="google">Google (Gemini)</option>
                            </TextField>

                            <TextField
                                select
                                fullWidth
                                label="Model"
                                margin="normal"
                                defaultValue="gpt-4"
                                SelectProps={{ native: true }}
                            >
                                <option value="gpt-4">GPT-4 Turbo</option>
                                <option value="gpt-3.5">GPT-3.5 Turbo</option>
                                <option value="claude-3-opus">Claude 3 Opus</option>
                                <option value="claude-3-sonnet">Claude 3 Sonnet</option>
                                <option value="mistral-large">Mistral Large</option>
                            </TextField>

                            <TextField
                                label="System Prompt"
                                fullWidth
                                margin="normal"
                                multiline
                                rows={4}
                                placeholder="Provide instructions that define the agent's behavior and capabilities..."
                            />
                        </Grid>
                    </Grid>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
                    <Button variant="contained" color="primary">
                        Create Agent
                    </Button>
                </DialogActions>
            </Dialog>

            {/* Delete Confirmation Dialog */}
            <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
                <DialogTitle>Confirm Deletion</DialogTitle>
                <DialogContent>
                    <Typography>
                        Are you sure you want to delete the agent "{selectedAgent?.name}"?
                        This action cannot be undone.
                    </Typography>
                    <Alert severity="warning" sx={{ mt: 2 }}>
                        All associated data and interactions will be permanently removed.
                    </Alert>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
                    <Button
                        onClick={handleDeleteConfirm}
                        variant="contained"
                        color="error"
                    >
                        Delete
                    </Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
};

export default Agents;
