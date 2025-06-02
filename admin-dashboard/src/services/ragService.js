import axios from 'axios';

const API_URL = '/api/system_engine';

const ragService = {
    /**
     * Get all documents
     */
    getDocuments: async (page = 1, limit = 10, filters = {}) => {
        const response = await axios.get(`${API_URL}/rag/documents`, {
            params: { page, limit, ...filters }
        });
        return response.data;
    },

    /**
     * Get document by ID
     */
    getDocument: async (id) => {
        const response = await axios.get(`${API_URL}/rag/documents/${id}`);
        return response.data;
    },

    /**
     * Upload a new document
     */
    uploadDocument: async (documentData) => {
        const formData = new FormData();

        // Handle file uploads
        if (documentData.file) {
            formData.append('file', documentData.file);
        }

        // Add metadata
        if (documentData.title) {
            formData.append('title', documentData.title);
        }

        if (documentData.metadata) {
            formData.append('metadata', JSON.stringify(documentData.metadata));
        }

        if (documentData.tags && Array.isArray(documentData.tags)) {
            documentData.tags.forEach(tag => {
                formData.append('tags', tag);
            });
        }

        const response = await axios.post(`${API_URL}/rag/documents/upload`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });

        return response.data;
    },

    /**
     * Update a document
     */
    updateDocument: async (id, documentData) => {
        const response = await axios.put(`${API_URL}/rag/documents/${id}`, documentData);
        return response.data;
    },

    /**
     * Delete a document
     */
    deleteDocument: async (id) => {
        const response = await axios.delete(`${API_URL}/rag/documents/${id}`);
        return response.data;
    },

    /**
     * Search documents using semantic search
     */
    searchDocuments: async (query, filters = {}, limit = 10) => {
        const response = await axios.post(`${API_URL}/rag/search`, {
            query,
            filters,
            limit
        });
        return response.data;
    },

    /**
     * Get document chunks
     */
    getDocumentChunks: async (documentId) => {
        const response = await axios.get(`${API_URL}/rag/documents/${documentId}/chunks`);
        return response.data;
    },

    /**
     * Regenerate embeddings for a document
     */
    regenerateEmbeddings: async (documentId) => {
        const response = await axios.post(`${API_URL}/rag/documents/${documentId}/embeddings`);
        return response.data;
    },

    /**
     * Get stats for RAG system
     */
    getRagStats: async () => {
        const response = await axios.get(`${API_URL}/rag/stats`);
        return response.data;
    }
};

export default ragService;
