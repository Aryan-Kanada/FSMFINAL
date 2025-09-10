import api from './api';

const BoxService = {
  // Get all boxes
  getAllBoxes: async () => {
    try {
      const response = await api.get('/boxes');
      return response.data;
    } catch (error) {
      console.error('Error fetching boxes:', error);
      throw error;
    }
  },

  // Get boxes with empty compartments
  getBoxesWithEmptyCompartments: async () => {
    try {
      const response = await api.get('/boxes/available');
      return response.data;
    } catch (error) {
      console.error('Error fetching available boxes:', error);
      throw error;
    }
  },

  // Get box by ID
  getBoxById: async (id) => {
    try {
      const response = await api.get(`/boxes/${id}`);
      if (response.data && response.data.length > 0) {
        return response.data[0];
      } else {
        throw new Error('Box not found');
      }
    } catch (error) {
      console.error(`Error fetching box ${id}:`, error);
      throw error;
    }
  },

  // Create new box
  createBox: async (boxData) => {
    try {
      const response = await api.post('/boxes', boxData);
      return response.data;
    } catch (error) {
      console.error('Error creating box:', error);
      // Log more details about the error response
      if (error.response) {
        console.error('Error response data:', error.response.data);
        console.error('Error response status:', error.response.status);
      }
      throw error;
    }
  },

  // Delete box
  deleteBox: async (id) => {
    try {
      const response = await api.delete(`/boxes/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error deleting box ${id}:`, error);
      throw error;
    }
  }
};

export default BoxService;
