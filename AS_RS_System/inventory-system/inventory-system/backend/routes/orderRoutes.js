
const express = require('express');
const OrderController = require('../controllers/orderController');

const router = express.Router();

// Get all orders
router.get('/', OrderController.getAllOrders);

// Get order statistics
router.get('/stats', OrderController.getOrderStats);

// Get orders by status
router.get('/status/:status', OrderController.getOrdersByStatus);

// Get order by ID
router.get('/:id', OrderController.getOrderById);

// Create new order
router.post('/', OrderController.createOrder);

// Update order status
router.patch('/:id/status', OrderController.updateOrderStatus);

module.exports = router;
