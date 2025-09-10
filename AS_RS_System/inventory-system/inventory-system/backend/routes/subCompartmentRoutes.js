const express = require('express');
const SubCompartmentController = require('../controllers/subCompartmentController');

const router = express.Router();

// Get all subcompartments
router.get('/', SubCompartmentController.getAllSubCompartments);

// Get subcompartment by place
router.get('/:place', SubCompartmentController.getSubCompartmentByPlace);

// Create new subcompartment
router.post('/', SubCompartmentController.createSubCompartment);

// Update subcompartment status
router.patch('/:place/status', SubCompartmentController.updateStatus);

// Delete subcompartment
router.delete('/:place', SubCompartmentController.deleteSubCompartment);

// Add product operation
router.post('/operations/add-product', SubCompartmentController.addProduct);

// Retrieve product operation
router.post('/operations/retrieve-product', SubCompartmentController.retrieveProduct);

module.exports = router;
