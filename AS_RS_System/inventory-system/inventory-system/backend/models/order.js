const db = require('../config/db');
const TransactionModel = require('./transaction');

class OrderModel {
  static async createOrder(orderData) {
    const connection = await db.getConnection();
    
    try {
      await connection.beginTransaction();
      
      // Calculate total amount if not provided
      let total_amount = orderData.total_amount;
      if (!total_amount && orderData.items) {
        total_amount = orderData.items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
      }
      
      // Insert order
      const [orderResult] = await connection.query(
        `INSERT INTO Orders (customer_name, customer_email, customer_phone, shipping_address, total_amount, order_status) 
         VALUES (?, ?, ?, ?, ?, ?)`,
        [
          orderData.customer_name,
          orderData.customer_email,
          orderData.customer_phone,
          orderData.shipping_address,
          total_amount,
          orderData.order_status || 'pending'
        ]
      );
      
      const orderId = orderResult.insertId;
      
      // Insert order items and update inventory
      if (orderData.items && orderData.items.length > 0) {
        const orderItemsValues = orderData.items.map(item => [
          orderId,
          item.item_id,
          item.quantity,
          item.price,
          item.quantity * item.price
        ]);
        
        await connection.query(
          `INSERT INTO OrderItems (order_id, item_id, quantity, unit_price, total_price) 
           VALUES ?`,
          [orderItemsValues]
        );
        
        // Check availability and update inventory for each ordered item
        for (const item of orderData.items) {
          // Check available inventory using SubCompartments
          const [inventoryRows] = await connection.query(`
            SELECT COUNT(*) as available_count
            FROM SubCompartments sc
            WHERE sc.item_id = ? AND sc.status = 'Occupied'
          `, [item.item_id]);
          
          const available = inventoryRows[0].available_count;
          
          if (available < item.quantity) {
            throw new Error(`Insufficient inventory for item ${item.item_id}. Available: ${available}, Requested: ${item.quantity}`);
          }
          
          // Reduce inventory by updating SubCompartments from Occupied to Empty
          // Get the occupied compartments for this item (column-wise priority)
          const [compartmentsToUpdate] = await connection.query(`
            SELECT sc.subcom_place
            FROM SubCompartments sc
            JOIN Boxes b ON sc.box_id = b.box_id
            WHERE sc.item_id = ? AND sc.status = 'Occupied'
            ORDER BY b.column_name, b.\`row_number\`, sc.sub_id
            LIMIT ?
          `, [item.item_id, item.quantity]);
          
          // Update these compartments to Empty and record transactions
          for (const compartment of compartmentsToUpdate) {
            // Update compartment status to Empty
            await connection.query(`
              UPDATE SubCompartments 
              SET status = 'Empty', item_id = NULL 
              WHERE subcom_place = ?
            `, [compartment.subcom_place]);
            
            // Record transaction for order fulfillment
            await connection.query(`
              INSERT INTO Transactions (item_id, subcom_place, action, time) 
              VALUES (?, ?, 'ordered', NOW())
            `, [item.item_id, compartment.subcom_place]);
          }
        }
      }
      
      await connection.commit();
      
      // Fetch the complete order data
      const [orders] = await connection.query(
        `SELECT o.*, 
                GROUP_CONCAT(
                  CONCAT(oi.quantity, 'x ', i.name) 
                  SEPARATOR ', '
                ) as items_summary
         FROM Orders o
         LEFT JOIN OrderItems oi ON o.order_id = oi.order_id
         LEFT JOIN Items i ON oi.item_id = i.item_id
         WHERE o.order_id = ?
         GROUP BY o.order_id`,
        [orderId]
      );
      
      return orders[0];
    } catch (error) {
      await connection.rollback();
      throw new Error(`Error creating order: ${error.message}`);
    } finally {
      connection.release();
    }
  }
  
  static async getAllOrders(limit = 100) {
    try {
      const [rows] = await db.query(
        `SELECT o.*, 
                GROUP_CONCAT(
                  CONCAT(oi.quantity, 'x ', i.name) 
                  SEPARATOR ', '
                ) as items_summary
         FROM Orders o
         LEFT JOIN OrderItems oi ON o.order_id = oi.order_id
         LEFT JOIN Items i ON oi.item_id = i.item_id
         GROUP BY o.order_id
         ORDER BY o.created_at DESC
         LIMIT ?`,
        [limit]
      );
      return rows;
    } catch (error) {
      throw new Error(`Error fetching orders: ${error.message}`);
    }
  }
  
  static async getOrderById(orderId) {
    try {
      const [orders] = await db.query(
        `SELECT o.* FROM Orders o WHERE o.order_id = ?`,
        [orderId]
      );
      
      if (orders.length === 0) {
        return null;
      }
      
      // Get order items
      const [orderItems] = await db.query(
        `SELECT oi.*, i.name as item_name, i.description as item_description
         FROM OrderItems oi
         JOIN Items i ON oi.item_id = i.item_id
         WHERE oi.order_id = ?`,
        [orderId]
      );
      
      return {
        ...orders[0],
        items: orderItems
      };
    } catch (error) {
      throw new Error(`Error fetching order by ID: ${error.message}`);
    }
  }
  
  static async updateOrderStatus(orderId, status) {
    try {
      const [result] = await db.query(
        `UPDATE Orders SET order_status = ?, updated_at = NOW() WHERE order_id = ?`,
        [status, orderId]
      );
      
      return { affectedRows: result.affectedRows };
    } catch (error) {
      throw new Error(`Error updating order status: ${error.message}`);
    }
  }
  
  static async getOrdersByStatus(status) {
    try {
      const [rows] = await db.query(
        `SELECT o.*, 
                GROUP_CONCAT(
                  CONCAT(oi.quantity, 'x ', i.name) 
                  SEPARATOR ', '
                ) as items_summary
         FROM Orders o
         LEFT JOIN OrderItems oi ON o.order_id = oi.order_id
         LEFT JOIN Items i ON oi.item_id = i.item_id
         WHERE o.order_status = ?
         GROUP BY o.order_id
         ORDER BY o.created_at DESC`,
        [status]
      );
      return rows;
    } catch (error) {
      throw new Error(`Error fetching orders by status: ${error.message}`);
    }
  }
  
  static async getOrderStats() {
    try {
      const [stats] = await db.query(`
        SELECT 
          COUNT(*) as total_orders,
          SUM(total_amount) as total_revenue,
          AVG(total_amount) as average_order_value,
          COUNT(CASE WHEN order_status = 'pending' THEN 1 END) as pending_orders,
          COUNT(CASE WHEN order_status = 'processing' THEN 1 END) as processing_orders,
          COUNT(CASE WHEN order_status = 'shipped' THEN 1 END) as shipped_orders,
          COUNT(CASE WHEN order_status = 'delivered' THEN 1 END) as delivered_orders,
          COUNT(CASE WHEN order_status = 'cancelled' THEN 1 END) as cancelled_orders
        FROM Orders
      `);
      
      return stats[0];
    } catch (error) {
      throw new Error(`Error fetching order statistics: ${error.message}`);
    }
  }
}

module.exports = OrderModel;
