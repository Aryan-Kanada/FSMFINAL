const express = require('express');
const BoxController = require('../controllers/boxController');

const router = express.Router();

// Get boxes with empty compartments
router.get('/available', BoxController.getBoxesWithEmptyCompartments);

// Get all boxes
router.get('/', BoxController.getAllBoxes);

// Get box by ID
router.get('/:id', BoxController.getBoxById);

// Create new box
router.post('/', BoxController.createBox);

// Delete box
router.delete('/:id', BoxController.deleteBox);

module.exports = router;
