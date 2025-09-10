import api from './api';

const ItemService = {
  // Get all items
  getAllItems: async () => {
    try {
      const response = await api.get('/items');
      return response.data;
    } catch (error) {
      console.error('Error fetching items:', error);
      throw error;
    }
  },

  // Get available items with count
  getAvailableItems: async () => {
    try {
      const response = await api.get('/items/available');
      return response.data;
    } catch (error) {
      console.error('Error fetching available items:', error);
      throw error;
    }
  },

  // Get item by ID
  getItemById: async (id) => {
    try {
      const response = await api.get(`/items/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching item ${id}:`, error);
      throw error;
    }
  },

  // Get item locations
  getItemLocations: async (id) => {
    try {
      const response = await api.get(`/items/${id}/locations`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching locations for item ${id}:`, error);
      throw error;
    }
  },

  // Create new item
  createItem: async (itemData) => {
    try {
      const response = await api.post('/items', itemData);
      return response.data;
    } catch (error) {
      console.error('Error creating item:', error);
      throw error;
    }
  },

  // Delete item
  deleteItem: async (id) => {
    try {
      const response = await api.delete(`/items/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error deleting item ${id}:`, error);
      throw error;
    }
  },

  // Check if item ID exists
  checkItemIdExists: async (id) => {
    try {
      const response = await api.get(`/items/check/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error checking item ID existence:`, error);
      throw error;
    }
  }
};

export default ItemService;
