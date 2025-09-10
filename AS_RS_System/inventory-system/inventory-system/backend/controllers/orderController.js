const OrderModel = require('../models/order');

class OrderController {
  // Create new order
  static async createOrder(req, res) {
    try {
      const { 
        customer_name, 
        customer_email, 
        customer_phone, 
        shipping_address, 
        items, 
        total_amount,
        order_status 
      } = req.body;
      
      // Validate required fields
      if (!customer_name || !customer_email || !customer_phone || !shipping_address) {
        return res.status(400).json({
          success: false,
          error: 'Please provide all required customer information'
        });
      }
      
      if (!items || !Array.isArray(items) || items.length === 0) {
        return res.status(400).json({
          success: false,
          error: 'Please provide order items'
        });
      }
      
      // Validate items structure
      for (const item of items) {
        if (!item.item_id || !item.quantity || !item.price || item.quantity <= 0 || item.price <= 0) {
          return res.status(400).json({
            success: false,
            error: 'Invalid item data. Each item must have item_id, quantity, and price'
          });
        }
      }
      
      const orderData = {
        customer_name,
        customer_email,
        customer_phone,
        shipping_address,
        items,
        total_amount, // Optional - will be calculated if not provided
        order_status: order_status || 'pending'
      };
      
      const order = await OrderModel.createOrder(orderData);
      
      res.status(201).json({
        success: true,
        message: 'Order created successfully',
        data: order
      });
    } catch (error) {
      console.error('Error in createOrder:', error);
      res.status(500).json({
        success: false,
        error: 'Server Error',
        message: error.message
      });
    }
  }
  
  // Get all orders
  static async getAllOrders(req, res) {
    try {
      const limit = parseInt(req.query.limit) || 100;
      const orders = await OrderModel.getAllOrders(limit);
      
      res.status(200).json({
        success: true,
        count: orders.length,
        data: orders
      });
    } catch (error) {
      console.error('Error in getAllOrders:', error);
      res.status(500).json({
        success: false,
        error: 'Server Error',
        message: error.message
      });
    }
  }
  
  // Get order by ID
  static async getOrderById(req, res) {
    try {
      const orderId = req.params.id;
      const order = await OrderModel.getOrderById(orderId);
      
      if (!order) {
        return res.status(404).json({
          success: false,
          error: 'Order not found'
        });
      }
      
      res.status(200).json({
        success: true,
        data: order
      });
    } catch (error) {
      console.error('Error in getOrderById:', error);
      res.status(500).json({
        success: false,
        error: 'Server Error',
        message: error.message
      });
    }
  }
  
  // Update order status
  static async updateOrderStatus(req, res) {
    try {
      const orderId = req.params.id;
      const { status } = req.body;
      
      if (!status) {
        return res.status(400).json({
          success: false,
          error: 'Please provide order status'
        });
      }
      
      const validStatuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled'];
      if (!validStatuses.includes(status)) {
        return res.status(400).json({
          success: false,
          error: 'Invalid order status'
        });
      }
      
      const result = await OrderModel.updateOrderStatus(orderId, status);
      
      if (result.affectedRows === 0) {
        return res.status(404).json({
          success: false,
          error: 'Order not found'
        });
      }
      
      res.status(200).json({
        success: true,
        message: `Order ${orderId} status updated to ${status}`
      });
    } catch (error) {
      console.error('Error in updateOrderStatus:', error);
      res.status(500).json({
        success: false,
        error: 'Server Error',
        message: error.message
      });
    }
  }
  
  // Get orders by status
  static async getOrdersByStatus(req, res) {
    try {
      const status = req.params.status;
      const validStatuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled'];
      
      if (!validStatuses.includes(status)) {
        return res.status(400).json({
          success: false,
          error: 'Invalid order status'
        });
      }
      
      const orders = await OrderModel.getOrdersByStatus(status);
      
      res.status(200).json({
        success: true,
        count: orders.length,
        data: orders
      });
    } catch (error) {
      console.error('Error in getOrdersByStatus:', error);
      res.status(500).json({
        success: false,
        error: 'Server Error',
        message: error.message
      });
    }
  }
  
  // Get order statistics
  static async getOrderStats(req, res) {
    try {
      const stats = await OrderModel.getOrderStats();
      
      res.status(200).json({
        success: true,
        data: stats
      });
    } catch (error) {
      console.error('Error in getOrderStats:', error);
      res.status(500).json({
        success: false,
        error: 'Server Error',
        message: error.message
      });
    }
  }
}

module.exports = OrderController;
