const express = require('express');
const ItemController = require('../controllers/itemController');

const router = express.Router();

// Get all items
router.get('/', ItemController.getAllItems);

// Get available items with count
router.get('/available', ItemController.getAvailableItems);

// Get item by ID
router.get('/:id', ItemController.getItemById);

// Get item locations
router.get('/:id/locations', ItemController.getItemLocations);

// Create new item
router.post('/', ItemController.createItem);

// Delete item
router.delete('/:id', ItemController.deleteItem);

module.exports = router;
