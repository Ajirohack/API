import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Button,
  TextField,
  Tabs,
  Tab,
  Card,
  CardContent,
  Divider,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  LinearProgress,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TableContainer,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  TablePagination
} from '@mui/material';
import {
  Search as SearchIcon,
  Upload as UploadIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  Download as DownloadIcon,
  Edit as EditIcon
} from '@mui/icons-material';

import ragService from '../services/ragService';

const TabPanel = (props) => {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`rag-tabpanel-${index}`}
      aria-labelledby={`rag-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ pt: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
};

const RagDashboard = () => {
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const [totalDocuments, setTotalDocuments] = useState(0);
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [documentFile, setDocumentFile] = useState(null);
  const [documentTitle, setDocumentTitle] = useState('');
  const [documentTags, setDocumentTags] = useState('');
  const [error, setError] = useState('');
  const [uploadProgress, setUploadProgress] = useState(0);

  useEffect(() => {
    fetchDocuments();
  }, [page, rowsPerPage]);

  const fetchDocuments = async () => {
    setLoading(true);
    try {
      // In a real app, replace this with actual API call:
      // const result = await ragService.getDocuments(page + 1, rowsPerPage);

      // Mock data for UI development
      await new Promise(resolve => setTimeout(resolve, 1000));
      const mockDocuments = [
        { id: '1', title: 'Company Policy Document', contentType: 'PDF', createdAt: '2023-10-15T10:30:00Z', metadata: { pageCount: 24 }, tags: ['policy', 'HR'] },
        { id: '2', title: 'Product Specifications', contentType: 'DOCX', createdAt: '2023-10-12T14:20:00Z', metadata: { version: '1.2.0' }, tags: ['product', 'technical'] },
        { id: '3', title: 'Customer Feedback Summary', contentType: 'TXT', createdAt: '2023-10-10T09:15:00Z', metadata: { customers: 42 }, tags: ['feedback', 'customers'] },
        { id: '4', title: 'Market Analysis 2023', contentType: 'PDF', createdAt: '2023-09-28T11:45:00Z', metadata: { author: 'Marketing Team' }, tags: ['market', 'analysis'] },
        { id: '5', title: 'Development Roadmap', contentType: 'MD', createdAt: '2023-09-22T16:10:00Z', metadata: { priority: 'HIGH' }, tags: ['development', 'planning'] },
        { id: '6', title: 'API Documentation', contentType: 'HTML', createdAt: '2023-09-15T13:25:00Z', metadata: { version: '3.1.4' }, tags: ['api', 'technical'] },
        { id: '7', title: 'Financial Report Q3', contentType: 'XLSX', createdAt: '2023-09-10T15:50:00Z', metadata: { confidential: true }, tags: ['financial', 'quarterly'] }
      ];

      setDocuments(mockDocuments);
      setTotalDocuments(15); // Mock total count
    } catch (err) {
      console.error('Error fetching documents:', err);
      setError('Failed to load documents');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    setLoading(true);
    try {
      // In a real app, replace this with actual API call:
      // const results = await ragService.searchDocuments(searchQuery);

      // Mock search results
      await new Promise(resolve => setTimeout(resolve, 1200));
      setSearchResults([
        {
          id: '1',
          chunkId: 'c1',
          title: 'Company Policy Document',
          content: 'The company policy dictates that all employees must complete annual security training...',
          score: 0.92,
          metadata: { page: 3 }
        },
        {
          id: '3',
          chunkId: 'c5',
          title: 'Customer Feedback Summary',
          content: 'Customers frequently mentioned security concerns in their feedback reports...',
          score: 0.85,
          metadata: { source: 'Customer Survey' }
        },
        {
          id: '5',
          chunkId: 'c12',
          title: 'Development Roadmap',
          content: 'Security improvements are scheduled for Q2, with a focus on user authentication...',
          score: 0.78,
          metadata: { milestone: 'Q2 2023' }
        }
      ]);
    } catch (err) {
      console.error('Search error:', err);
      setError('Search failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleOpenUploadDialog = () => {
    setUploadDialogOpen(true);
    setDocumentFile(null);
    setDocumentTitle('');
    setDocumentTags('');
    setError('');
  };

  const handleCloseUploadDialog = () => {
    setUploadDialogOpen(false);
  };

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setDocumentFile(file);
      // Auto-populate title from filename if empty
      if (!documentTitle) {
        setDocumentTitle(file.name.split('.')[0]);
      }
    }
  };

  const handleUpload = async () => {
    if (!documentFile) {
      setError('Please select a file to upload');
      return;
    }

    if (!documentTitle.trim()) {
      setError('Please provide a document title');
      return;
    }

    const formData = {
      file: documentFile,
      title: documentTitle,
      tags: documentTags.split(',').map(tag => tag.trim()).filter(tag => tag)
    };

    setLoading(true);
    // Simulate upload progress
    const progressInterval = setInterval(() => {
      setUploadProgress(prev => {
        const newProgress = prev + 20;
        return newProgress >= 100 ? 100 : newProgress;
      });
    }, 500);

    try {
      // In a real app, call the actual API:
      // await ragService.uploadDocument(formData);

      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2500));

      // Refresh document list
      fetchDocuments();
      handleCloseUploadDialog();
    } catch (err) {
      console.error('Upload error:', err);
      setError('Failed to upload document. Please try again.');
    } finally {
      clearInterval(progressInterval);
      setUploadProgress(0);
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        RAG System
      </Typography>

      <Paper sx={{ mb: 4 }}>
        <Tabs value={tabValue} onChange={handleTabChange} centered>
          <Tab label="Search Knowledge Base" />
          <Tab label="Manage Documents" />
          <Tab label="System Settings" />
        </Tabs>

        {/* Search Tab */}
        <TabPanel value={tabValue} index={0}>
          <Box sx={{ p: 2 }}>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} md={10}>
                <TextField
                  fullWidth
                  variant="outlined"
                  placeholder="Search the knowledge base..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                />
              </Grid>
              <Grid item xs={12} md={2}>
                <Button
                  fullWidth
                  variant="contained"
                  startIcon={<SearchIcon />}
                  onClick={handleSearch}
                  disabled={loading || !searchQuery.trim()}
                >
                  Search
                </Button>
              </Grid>
            </Grid>

            {loading && <LinearProgress sx={{ mt: 2 }} />}

            {error && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {error}
              </Alert>
            )}

            {/* Search Results */}
            {searchResults.length > 0 && (
              <Box sx={{ mt: 4 }}>
                <Typography variant="h6" gutterBottom>
                  Search Results
                </Typography>
                <List>
                  {searchResults.map((result, index) => (
                    <React.Fragment key={result.chunkId}>
                      {index > 0 && <Divider />}
                      <ListItem alignItems="flex-start">
                        <ListItemText
                          primary={
                            <Box display="flex" justifyContent="space-between" alignItems="center">
                              <Typography variant="subtitle1">
                                {result.title}
                              </Typography>
                              <Chip
                                label={`Relevance: ${(result.score * 100).toFixed(0)}%`}
                                color={result.score > 0.9 ? 'success' : result.score > 0.7 ? 'primary' : 'default'}
                                size="small"
                              />
                            </Box>
                          }
                          secondary={
                            <React.Fragment>
                              <Typography variant="body2" color="text.primary" sx={{ mt: 1 }}>
                                {result.content}
                              </Typography>
                              <Box sx={{ mt: 1, display: 'flex', justifyContent: 'space-between' }}>
                                <Typography variant="caption" color="text.secondary">
                                  {result.metadata && Object.entries(result.metadata).map(([key, value]) =>
                                    `${key}: ${value}`
                                  ).join(' • ')}
                                </Typography>
                                <Button size="small">View Document</Button>
                              </Box>
                            </React.Fragment>
                          }
                        />
                      </ListItem>
                    </React.Fragment>
                  ))}
                </List>
              </Box>
            )}

            {/* Empty State */}
            {!loading && searchResults.length === 0 && searchQuery.trim() && (
              <Box sx={{ mt: 4, p: 3, textAlign: 'center' }}>
                <Typography variant="body1" color="text.secondary">
                  No results found for your query. Try different keywords or add more documents to the knowledge base.
                </Typography>
              </Box>
            )}
          </Box>
        </TabPanel>

        {/* Document Management Tab */}
        <TabPanel value={tabValue} index={1}>
          <Box sx={{ p: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
              <Typography variant="h6">Document Library</Typography>
              <Box>
                <Button
                  variant="outlined"
                  startIcon={<RefreshIcon />}
                  onClick={fetchDocuments}
                  sx={{ mr: 1 }}
                >
                  Refresh
                </Button>
                <Button
                  variant="contained"
                  startIcon={<UploadIcon />}
                  onClick={handleOpenUploadDialog}
                >
                  Upload Document
                </Button>
              </Box>
            </Box>

            {loading && <LinearProgress sx={{ mb: 2 }} />}

            {/* Document Table */}
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Title</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Tags</TableCell>
                    <TableCell>Created</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {documents.map((doc) => (
                    <TableRow key={doc.id}>
                      <TableCell>{doc.title}</TableCell>
                      <TableCell>{doc.contentType}</TableCell>
                      <TableCell>
                        {doc.tags.map(tag => (
                          <Chip key={tag} label={tag} size="small" sx={{ mr: 0.5 }} />
                        ))}
                      </TableCell>
                      <TableCell>{formatDate(doc.createdAt)}</TableCell>
                      <TableCell>
                        <IconButton size="small" title="Edit">
                          <EditIcon fontSize="small" />
                        </IconButton>
                        <IconButton size="small" title="Download">
                          <DownloadIcon fontSize="small" />
                        </IconButton>
                        <IconButton size="small" title="Delete">
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>

            <TablePagination
              component="div"
              count={totalDocuments}
              page={page}
              onPageChange={handleChangePage}
              rowsPerPage={rowsPerPage}
              onRowsPerPageChange={handleChangeRowsPerPage}
            />

            {/* Empty state */}
            {!loading && documents.length === 0 && (
              <Box sx={{ mt: 4, p: 3, textAlign: 'center' }}>
                <Typography variant="body1" color="text.secondary">
                  No documents found. Upload your first document to get started.
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={handleOpenUploadDialog}
                  sx={{ mt: 2 }}
                >
                  Add Document
                </Button>
              </Box>
            )}
          </Box>
        </TabPanel>

        {/* Settings Tab */}
        <TabPanel value={tabValue} index={2}>
          <Box sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              RAG System Configuration
            </Typography>

            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      Embedding Model
                    </Typography>
                    <FormControl fullWidth sx={{ mt: 2 }}>
                      <InputLabel>Model</InputLabel>
                      <Select
                        value="openai-ada-002"
                        label="Model"
                      >
                        <MenuItem value="openai-ada-002">OpenAI Ada 002</MenuItem>
                        <MenuItem value="openai-text-embedding-3-small">OpenAI Text Embedding 3 Small</MenuItem>
                        <MenuItem value="huggingface-mpnet">HuggingFace MPNet</MenuItem>
                        <MenuItem value="sbert-mpnet">SBERT MPNet</MenuItem>
                      </Select>
                    </FormControl>

                    <Typography variant="subtitle1" gutterBottom sx={{ mt: 3 }}>
                      Chunking Settings
                    </Typography>
                    <Grid container spacing={2}>
                      <Grid item xs={6}>
                        <TextField
                          fullWidth
                          label="Chunk Size"
                          type="number"
                          defaultValue={512}
                          helperText="Tokens per chunk"
                        />
                      </Grid>
                      <Grid item xs={6}>
                        <TextField
                          fullWidth
                          label="Chunk Overlap"
                          type="number"
                          defaultValue={64}
                          helperText="Overlap tokens"
                        />
                      </Grid>
                    </Grid>

                    <Box sx={{ mt: 3 }}>
                      <Button variant="contained">Save Settings</Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      Vector Database
                    </Typography>

                    <FormControl fullWidth sx={{ mt: 2 }}>
                      <InputLabel>Database Type</InputLabel>
                      <Select
                        value="postgres"
                        label="Database Type"
                      >
                        <MenuItem value="postgres">PostgreSQL with pgvector</MenuItem>
                        <MenuItem value="qdrant">Qdrant</MenuItem>
                        <MenuItem value="pinecone">Pinecone</MenuItem>
                        <MenuItem value="redis">Redis</MenuItem>
                      </Select>
                    </FormControl>

                    <TextField
                      fullWidth
                      label="Connection String"
                      margin="normal"
                      defaultValue="postgresql://user:password@db:5432/spacedb"
                      type="password"
                    />

                    <Box sx={{ mt: 3, display: 'flex', justifyContent: 'space-between' }}>
                      <Button variant="outlined" color="error">
                        Rebuild Index
                      </Button>
                      <Button variant="contained">
                        Test Connection
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Box>
        </TabPanel>
      </Paper>

      {/* Upload Dialog */}
      <Dialog open={uploadDialogOpen} onClose={handleCloseUploadDialog} fullWidth maxWidth="sm">
        <DialogTitle>Upload New Document</DialogTitle>
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Button
            variant="outlined"
            component="label"
            fullWidth
            sx={{ mt: 2, p: 3, border: '1px dashed' }}
          >
            {documentFile ? documentFile.name : 'Choose File'}
            <input
              type="file"
              hidden
              onChange={handleFileChange}
              accept=".pdf,.doc,.docx,.txt,.md,.html,.json"
            />
          </Button>

          <TextField
            margin="normal"
            label="Document Title"
            fullWidth
            value={documentTitle}
            onChange={(e) => setDocumentTitle(e.target.value)}
          />

          <TextField
            margin="normal"
            label="Tags (comma separated)"
            fullWidth
            value={documentTags}
            onChange={(e) => setDocumentTags(e.target.value)}
            placeholder="technical, policy, report"
          />

          {uploadProgress > 0 && (
            <Box sx={{ width: '100%', mt: 2 }}>
              <LinearProgress variant="determinate" value={uploadProgress} />
              <Typography variant="caption" align="center" display="block" sx={{ mt: 1 }}>
                Processing document...
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseUploadDialog} disabled={loading}>Cancel</Button>
          <Button
            onClick={handleUpload}
            variant="contained"
            disabled={loading || !documentFile}
          >
            {loading ? 'Uploading...' : 'Upload'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default RagDashboard;
