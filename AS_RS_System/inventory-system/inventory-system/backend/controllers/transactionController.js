const TransactionModel = require('../models/transaction');

class TransactionController {
  // Get all transactions with optional sorting
  static async getAllTransactions(req, res) {
    try {
      const { sort = 'id_asc', limit = 100 } = req.query;
      const transactions = await TransactionModel.getAllTransactions(sort, limit);
      
      res.status(200).json({
        success: true,
        count: transactions.length,
        data: transactions
      });
    } catch (error) {
      console.error('Error in getAllTransactions:', error);
      res.status(500).json({
        success: false,
        error: 'Server Error',
        message: error.message
      });
    }
  }

  // Get transaction by ID
  static async getTransactionById(req, res) {
    try {
      const transaction = await TransactionModel.getTransactionById(req.params.id);
      
      if (!transaction) {
        return res.status(404).json({
          success: false,
          error: 'Transaction not found'
        });
      }
      
      res.status(200).json({
        success: true,
        data: transaction
      });
    } catch (error) {
      console.error('Error in getTransactionById:', error);
      res.status(500).json({
        success: false,
        error: 'Server Error',
        message: error.message
      });
    }
  }

  // Get transactions by item ID
  static async getTransactionsByItemId(req, res) {
    try {
      const transactions = await TransactionModel.getTransactionsByItemId(req.params.itemId);
      
      res.status(200).json({
        success: true,
        count: transactions.length,
        data: transactions
      });
    } catch (error) {
      console.error('Error in getTransactionsByItemId:', error);
      res.status(500).json({
        success: false,
        error: 'Server Error',
        message: error.message
      });
    }
  }
}

module.exports = TransactionController;
