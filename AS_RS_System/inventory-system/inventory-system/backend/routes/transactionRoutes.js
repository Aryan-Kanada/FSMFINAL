const express = require('express');
const TransactionController = require('../controllers/transactionController');

const router = express.Router();

// Get all transactions with optional sorting
router.get('/', TransactionController.getAllTransactions);

// Get transaction by ID
router.get('/:id', TransactionController.getTransactionById);

// Get transactions by item ID
router.get('/item/:itemId', TransactionController.getTransactionsByItemId);

module.exports = router;
