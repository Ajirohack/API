import axios from 'axios';

const API_URL = '/api/system_engine';

const pluginService = {
    /**
     * Get all plugins
     */
    getPlugins: async () => {
        const response = await axios.get(`${API_URL}/plugins`);
        return response.data;
    },

    /**
     * Get plugin by ID
     */
    getPlugin: async (id) => {
        const response = await axios.get(`${API_URL}/plugins/${id}`);
        return response.data;
    },

    /**
     * Install a new plugin
     */
    installPlugin: async (pluginData) => {
        const response = await axios.post(`${API_URL}/plugins/install`, pluginData);
        return response.data;
    },

    /**
     * Update a plugin
     */
    updatePlugin: async (id, pluginData) => {
        const response = await axios.put(`${API_URL}/plugins/${id}`, pluginData);
        return response.data;
    },

    /**
     * Enable a plugin
     */
    enablePlugin: async (id) => {
        const response = await axios.post(`${API_URL}/plugins/${id}/enable`);
        return response.data;
    },

    /**
     * Disable a plugin
     */
    disablePlugin: async (id) => {
        const response = await axios.post(`${API_URL}/plugins/${id}/disable`);
        return response.data;
    },

    /**
     * Uninstall a plugin
     */
    uninstallPlugin: async (id) => {
        const response = await axios.delete(`${API_URL}/plugins/${id}`);
        return response.data;
    }
};

export default pluginService;
