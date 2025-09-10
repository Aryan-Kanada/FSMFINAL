const SubCompartmentModel = require('../models/subCompartment');

class SubCompartmentController {
  // Get all subcompartments
  static async getAllSubCompartments(req, res) {
    try {
      const subCompartments = await SubCompartmentModel.getAllSubCompartments();
      res.status(200).json({
        success: true,
        count: subCompartments.length,
        data: subCompartments
      });
    } catch (error) {
      console.error('Error in getAllSubCompartments:', error);
      res.status(500).json({
        success: false,
        error: 'Server Error',
        message: error.message
      });
    }
  }

  // Get subcompartment by place
  static async getSubCompartmentByPlace(req, res) {
    try {
      const subCompartment = await SubCompartmentModel.getSubCompartmentByPlace(req.params.place);
      
      if (!subCompartment) {
        return res.status(404).json({
          success: false,
          error: 'SubCompartment not found'
        });
      }
      
      res.status(200).json({
        success: true,
        data: subCompartment
      });
    } catch (error) {
      console.error('Error in getSubCompartmentByPlace:', error);
      res.status(500).json({
        success: false,
        error: 'Server Error',
        message: error.message
      });
    }
  }

  // Create new subcompartment
  static async createSubCompartment(req, res) {
    try {
      const { boxId, subId, itemId, status } = req.body;
      
      if (!boxId || !subId || !status) {
        return res.status(400).json({
          success: false,
          error: 'Please provide boxId, subId, and status'
        });
      }
      
      // Generate subcom_place
      const subcomPlace = `${boxId}${subId}`;
      
      const subCompartment = await SubCompartmentModel.createSubCompartment(
        subcomPlace, boxId, subId, itemId, status
      );
      
      res.status(201).json({
        success: true,
        data: subCompartment
      });
    } catch (error) {
      console.error('Error in createSubCompartment:', error);
      res.status(500).json({
        success: false,
        error: 'Server Error',
        message: error.message
      });
    }
  }

  // Update subcompartment status
  static async updateStatus(req, res) {
    try {
      const { place } = req.params;
      const { status, itemId } = req.body;
      
      if (!status) {
        return res.status(400).json({
          success: false,
          error: 'Please provide status'
        });
      }
      
      const result = await SubCompartmentModel.updateStatus(place, status, itemId);
      
      if (result.affectedRows === 0) {
        return res.status(404).json({
          success: false,
          error: 'SubCompartment not found'
        });
      }
      
      res.status(200).json({
        success: true,
        data: result
      });
    } catch (error) {
      console.error('Error in updateStatus:', error);
      res.status(500).json({
        success: false,
        error: 'Server Error',
        message: error.message
      });
    }
  }

  // Delete subcompartment
  static async deleteSubCompartment(req, res) {
    try {
      const result = await SubCompartmentModel.deleteSubCompartment(req.params.place);
      
      if (result.affectedRows === 0) {
        return res.status(404).json({
          success: false,
          error: 'SubCompartment not found'
        });
      }
      
      res.status(200).json({
        success: true,
        message: `SubCompartment ${req.params.place} deleted`
      });
    } catch (error) {
      console.error('Error in deleteSubCompartment:', error);
      res.status(500).json({
        success: false,
        error: 'Server Error',
        message: error.message
      });
    }
  }

  // Add product to storage
  static async addProduct(req, res) {
    try {
      const { boxId, subId, itemId } = req.body;
      
      if (!boxId || !subId || !itemId) {
        return res.status(400).json({
          success: false,
          error: 'Please provide boxId, subId, and itemId'
        });
      }
      
      const result = await SubCompartmentModel.addProduct(boxId, subId, itemId);
      
      res.status(201).json({
        success: true,
        data: result
      });
    } catch (error) {
      console.error('Error in addProduct:', error);
      res.status(500).json({
        success: false,
        error: 'Server Error',
        message: error.message
      });
    }
  }

  // Retrieve product from storage
  static async retrieveProduct(req, res) {
    try {
      const { itemId, quantity } = req.body;
      
      if (!itemId || !quantity) {
        return res.status(400).json({
          success: false,
          error: 'Please provide itemId and quantity'
        });
      }
      
      const result = await SubCompartmentModel.retrieveProduct(itemId, quantity);
      
      res.status(200).json({
        success: true,
        data: result
      });
    } catch (error) {
      console.error('Error in retrieveProduct:', error);
      res.status(500).json({
        success: false,
        error: 'Server Error',
        message: error.message
      });
    }
  }
}

module.exports = SubCompartmentController;
