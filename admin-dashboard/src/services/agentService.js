import axios from 'axios';

const API_URL = '/api/system_engine';

const agentService = {
    /**
     * Get all agents
     */
    getAgents: async () => {
        const response = await axios.get(`${API_URL}/agents`);
        return response.data;
    },

    /**
     * Get agent by ID
     */
    getAgent: async (id) => {
        const response = await axios.get(`${API_URL}/agents/${id}`);
        return response.data;
    },

    /**
     * Create a new agent
     */
    createAgent: async (agentData) => {
        const response = await axios.post(`${API_URL}/agents`, agentData);
        return response.data;
    },

    /**
     * Update an agent
     */
    updateAgent: async (id, agentData) => {
        const response = await axios.put(`${API_URL}/agents/${id}`, agentData);
        return response.data;
    },

    /**
     * Delete an agent
     */
    deleteAgent: async (id) => {
        const response = await axios.delete(`${API_URL}/agents/${id}`);
        return response.data;
    },

    /**
     * Get agent interactions/history
     */
    getAgentInteractions: async (id, page = 1, limit = 10) => {
        const response = await axios.get(`${API_URL}/agents/${id}/interactions`, {
            params: { page, limit }
        });
        return response.data;
    },

    /**
     * Test an agent with sample input
     */
    testAgent: async (id, testInput) => {
        const response = await axios.post(`${API_URL}/agents/${id}/test`, testInput);
        return response.data;
    },

    /**
     * Get available agent templates
     */
    getAgentTemplates: async () => {
        const response = await axios.get(`${API_URL}/agents/templates`);
        return response.data;
    }
};

export default agentService;
