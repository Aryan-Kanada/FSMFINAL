const ItemModel = require('../models/item');

class ItemController {
  // Get all items
  static async getAllItems(req, res) {
    try {
      const items = await ItemModel.getAllItems();
      res.status(200).json({
        success: true,
        count: items.length,
        data: items
      });
    } catch (error) {
      console.error('Error in getAllItems:', error);
      res.status(500).json({
        success: false,
        error: 'Server Error',
        message: error.message
      });
    }
  }

  // Get item by ID
  static async getItemById(req, res) {
    try {
      const item = await ItemModel.getItemById(req.params.id);
      
      if (!item) {
        return res.status(404).json({
          success: false,
          error: 'Item not found'
        });
      }
      
      res.status(200).json({
        success: true,
        data: item
      });
    } catch (error) {
      console.error('Error in getItemById:', error);
      res.status(500).json({
        success: false,
        error: 'Server Error',
        message: error.message
      });
    }
  }

  // Create new item
  static async createItem(req, res) {
    try {
      const { item_id, name, description } = req.body;
      
      if (!name) {
        return res.status(400).json({
          success: false,
          error: 'Please provide a name'
        });
      }

      if (!item_id) {
        return res.status(400).json({
          success: false,
          error: 'Please provide an item ID'
        });
      }

      // Check if item ID already exists
      const idExists = await ItemModel.checkItemIdExists(item_id);
      if (idExists) {
        return res.status(400).json({
          success: false,
          error: 'Item ID already exists'
        });
      }
      
      const item = await ItemModel.createItem(item_id, name, description || '');
      
      res.status(201).json({
        success: true,
        data: item
      });
    } catch (error) {
      console.error('Error in createItem:', error);
      res.status(500).json({
        success: false,
        error: 'Server Error',
        message: error.message
      });
    }
  }

  // Delete item
  static async deleteItem(req, res) {
    try {
      const result = await ItemModel.deleteItem(req.params.id);
      
      if (result.affectedRows === 0) {
        return res.status(404).json({
          success: false,
          error: 'Item not found'
        });
      }
      
      res.status(200).json({
        success: true,
        message: `Item ${req.params.id} deleted`
      });
    } catch (error) {
      console.error('Error in deleteItem:', error);
      res.status(500).json({
        success: false,
        error: 'Server Error',
        message: error.message
      });
    }
  }

  // Get available items with count
  static async getAvailableItems(req, res) {
    try {
      const items = await ItemModel.getAvailableItemsWithCount();
      res.status(200).json({
        success: true,
        count: items.length,
        data: items
      });
    } catch (error) {
      console.error('Error in getAvailableItems:', error);
      res.status(500).json({
        success: false,
        error: 'Server Error',
        message: error.message
      });
    }
  }

  // Get item locations
  static async getItemLocations(req, res) {
    try {
      const itemId = req.params.id;
      const locations = await ItemModel.getItemLocations(itemId);
      
      res.status(200).json({
        success: true,
        count: locations.length,
        data: locations
      });
    } catch (error) {
      console.error('Error in getItemLocations:', error);
      res.status(500).json({
        success: false,
        error: 'Server Error',
        message: error.message
      });
    }
  }

  // Check if item ID exists
  static async checkItemIdExists(req, res) {
    try {
      const itemId = req.params.id;
      const exists = await ItemModel.checkItemIdExists(itemId);
      
      res.status(200).json({
        success: true,
        exists: exists
      });
    } catch (error) {
      console.error('Error in checkItemIdExists:', error);
      res.status(500).json({
        success: false,
        error: 'Server Error',
        message: error.message
      });
    }
  }
}

module.exports = ItemController;
