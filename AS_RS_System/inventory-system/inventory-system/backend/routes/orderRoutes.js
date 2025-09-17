// routes/orderRoutes.js

const express = require('express');
const { body, validationResult } = require('express-validator');
const OrderController = require('../controllers/orderController');

const router = express.Router();

// Validation middleware for creating orders
const validateOrder = [
  body('customer_name').notEmpty().withMessage('Customer name is required'),
  body('customer_email').isEmail().withMessage('Valid email is required'),
  body('customer_phone').notEmpty().withMessage('Customer phone is required'),
  body('shipping_address').notEmpty().withMessage('Shipping address is required'),
  body('items').isArray({ min: 1 }).withMessage('At least one order item is required'),
  body('items.*.item_id').notEmpty().withMessage('Item ID is required'),
  body('items.*.quantity').isInt({ gt: 0 }).withMessage('Quantity must be greater than zero'),
  body('items.*.price').isFloat({ gt: 0 }).withMessage('Price must be greater than zero')
];

// Create new order with validation
router.post(
  '/',
  validateOrder,
  (req, res, next) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ success: false, errors: errors.array() });
    }
    next();
  },
  OrderController.createOrder
);

// Get all orders
router.get('/', OrderController.getAllOrders);

// Get order statistics
router.get('/stats', OrderController.getOrderStats);

// Get orders by status
router.get('/status/:status', OrderController.getOrdersByStatus);

// Get order by ID
router.get('/:id', OrderController.getOrderById);

// Update order status
router.patch('/:id/status', OrderController.updateOrderStatus);

module.exports = router;
