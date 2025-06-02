import axios from 'axios';

const API_URL = '/api/system_engine';

const workflowService = {
    /**
     * Get all workflows
     */
    getWorkflows: async () => {
        const response = await axios.get(`${API_URL}/workflows`);
        return response.data;
    },

    /**
     * Get workflow by ID
     */
    getWorkflow: async (id) => {
        const response = await axios.get(`${API_URL}/workflows/${id}`);
        return response.data;
    },

    /**
     * Create a new workflow
     */
    createWorkflow: async (workflowData) => {
        const response = await axios.post(`${API_URL}/workflows`, workflowData);
        return response.data;
    },

    /**
     * Update a workflow
     */
    updateWorkflow: async (id, workflowData) => {
        const response = await axios.put(`${API_URL}/workflows/${id}`, workflowData);
        return response.data;
    },

    /**
     * Delete a workflow
     */
    deleteWorkflow: async (id) => {
        const response = await axios.delete(`${API_URL}/workflows/${id}`);
        return response.data;
    },

    /**
     * Execute a workflow
     */
    executeWorkflow: async (id, params = {}) => {
        const response = await axios.post(`${API_URL}/workflows/${id}/execute`, params);
        return response.data;
    },

    /**
     * Get workflow execution history
     */
    getWorkflowExecutions: async (id, page = 1, limit = 10) => {
        const response = await axios.get(`${API_URL}/workflows/${id}/executions`, {
            params: { page, limit }
        });
        return response.data;
    },

    /**
     * Get a specific workflow execution
     */
    getWorkflowExecution: async (workflowId, executionId) => {
        const response = await axios.get(`${API_URL}/workflows/${workflowId}/executions/${executionId}`);
        return response.data;
    }
};

export default workflowService;
