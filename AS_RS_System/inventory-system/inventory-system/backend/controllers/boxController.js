const BoxModel = require('../models/box');

class BoxController {
  // Get boxes with empty compartments
  static async getBoxesWithEmptyCompartments(req, res) {
    try {
      const boxes = await BoxModel.getBoxesWithEmptyCompartments();
      res.status(200).json({
        success: true,
        count: boxes.length,
        data: boxes
      });
    } catch (error) {
      console.error('Error in getBoxesWithEmptyCompartments:', error);
      res.status(500).json({
        success: false,
        error: 'Server Error',
        message: error.message
      });
    }
  }

  // Get all boxes
  static async getAllBoxes(req, res) {
    try {
      const boxes = await BoxModel.getAllBoxes();
      res.status(200).json({
        success: true,
        count: boxes.length,
        data: boxes
      });
    } catch (error) {
      console.error('Error in getAllBoxes:', error);
      res.status(500).json({
        success: false,
        error: 'Server Error',
        message: error.message
      });
    }
  }

  // Get box by ID
  static async getBoxById(req, res) {
    try {
      const box = await BoxModel.getBoxById(req.params.id);
      
      if (!box) {
        return res.status(404).json({
          success: false,
          error: 'Box not found'
        });
      }
      
      res.status(200).json({
        success: true,
        data: box
      });
    } catch (error) {
      console.error('Error in getBoxById:', error);
      res.status(500).json({
        success: false,
        error: 'Server Error',
        message: error.message
      });
    }
  }

  // Create new box
  static async createBox(req, res) {
    try {
      const { boxId, columnName, rowNumber } = req.body;
      
      if (!boxId || !columnName || rowNumber === undefined) {
        return res.status(400).json({
          success: false,
          error: 'Please provide boxId, columnName and rowNumber'
        });
      }
      
      const box = await BoxModel.createBox(boxId, columnName, rowNumber);
      
      res.status(201).json({
        success: true,
        data: box
      });
    } catch (error) {
      console.error('Error in createBox:', error);
      res.status(500).json({
        success: false,
        error: 'Server Error',
        message: error.message
      });
    }
  }

  // Delete box
  static async deleteBox(req, res) {
    try {
      const result = await BoxModel.deleteBox(req.params.id);
      
      if (result.affectedRows === 0) {
        return res.status(404).json({
          success: false,
          error: 'Box not found'
        });
      }
      
      res.status(200).json({
        success: true,
        message: `Box ${req.params.id} deleted`
      });
    } catch (error) {
      console.error('Error in deleteBox:', error);
      res.status(500).json({
        success: false,
        error: 'Server Error',
        message: error.message
      });
    }
  }
}

module.exports = BoxController;
