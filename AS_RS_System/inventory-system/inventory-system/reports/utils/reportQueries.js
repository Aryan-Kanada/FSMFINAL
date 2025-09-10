const { pool } = require('../config/db');

class ReportQueries {
  static async getInventoryStatusByDateRange(startDate, endDate) {
    try {
      const query = `
        SELECT 
          i.item_id,
          i.name,
          i.description,
          COUNT(DISTINCT sc.subcom_place) as total_quantity,
          COUNT(DISTINCT CASE WHEN sc.item_id IS NOT NULL THEN sc.subcom_place END) as occupied_quantity,
          COUNT(DISTINCT CASE WHEN sc.item_id IS NULL THEN sc.subcom_place END) as available_quantity,
          MAX(t.time) as last_updated
        FROM Items i
        LEFT JOIN SubCompartments sc ON i.item_id = sc.item_id 
        LEFT JOIN Transactions t ON i.item_id = t.item_id 
          AND t.time BETWEEN ? AND ?
        GROUP BY i.item_id, i.name, i.description
        ORDER BY i.name
      `;
      
      const [rows] = await pool.execute(query, [startDate, endDate]);
      return rows;
    } catch (error) {
      throw new Error(`Error fetching inventory status: ${error.message}`);
    }
  }

  static async getTransactionsByDateRange(startDate, endDate) {
    try {
      const query = `
        SELECT 
          t.tran_id,
          t.item_id,
          i.name as item_name,
          t.subcom_place,
          t.action,
          t.time
        FROM Transactions t
        LEFT JOIN Items i ON t.item_id = i.item_id
        WHERE t.time BETWEEN ? AND ?
        ORDER BY t.time DESC
      `;
      
      const [rows] = await pool.execute(query, [startDate, endDate]);
      return rows;
    } catch (error) {
      throw new Error(`Error fetching transactions: ${error.message}`);
    }
  }

  static async getBoxUtilizationByDateRange(startDate, endDate) {
    try {
      const query = `
        SELECT 
          b.box_id,
          CONCAT(b.column_name, b.row_number) as location,
          COUNT(DISTINCT sc.subcom_place) as total_compartments,
          COUNT(DISTINCT CASE WHEN sc.item_id IS NOT NULL THEN sc.subcom_place END) as occupied_compartments,
          COUNT(DISTINCT CASE WHEN sc.item_id IS NULL THEN sc.subcom_place END) as available_compartments
        FROM Boxes b
        LEFT JOIN SubCompartments sc ON b.box_id = sc.box_id
        GROUP BY b.box_id, b.column_name, b.row_number
        ORDER BY b.box_id
      `;
      
      const [rows] = await pool.execute(query);
      return rows;
    } catch (error) {
      console.error('Database query error:', error);
      throw new Error(`Error fetching box utilization: ${error.message}`);
    }
  }

  static async getTopActiveItems(startDate, endDate, limit = 10) {
    try {
      const query = `
        SELECT 
          i.item_id,
          i.name as item_name,
          COUNT(*) as total_activities,
          COUNT(CASE WHEN t.action = 'added' THEN 1 END) as additions,
          COUNT(CASE WHEN t.action = 'retrieved' THEN 1 END) as retrievals
        FROM Transactions t
        LEFT JOIN Items i ON t.item_id = i.item_id
        WHERE t.time BETWEEN ? AND ?
        GROUP BY i.item_id, i.name
        ORDER BY total_activities DESC
        LIMIT ${parseInt(limit)}
      `;
      
      const [rows] = await pool.execute(query, [startDate, endDate]);
      return rows;
    } catch (error) {
      throw new Error(`Error fetching top active items: ${error.message}`);
    }
  }

  static async getSystemSummary(startDate, endDate) {
    try {
      const queries = {
        totalItems: `SELECT COUNT(*) as count FROM Items`,
        totalBoxes: `SELECT COUNT(*) as count FROM Boxes`,
        totalCompartments: `SELECT COUNT(*) as count FROM SubCompartments`,
        occupiedCompartments: `SELECT COUNT(*) as count FROM SubCompartments WHERE item_id IS NOT NULL`,
        transactionsInPeriod: `SELECT COUNT(*) as count FROM Transactions WHERE time BETWEEN ? AND ?`,
        additionsInPeriod: `SELECT COUNT(*) as count FROM Transactions WHERE time BETWEEN ? AND ? AND action = 'added'`,
        retrievalsInPeriod: `SELECT COUNT(*) as count FROM Transactions WHERE time BETWEEN ? AND ? AND action = 'retrieved'`
      };

      const results = {};
      
      // Execute queries that don't need date parameters
      const [totalItemsResult] = await pool.execute(queries.totalItems);
      const [totalBoxesResult] = await pool.execute(queries.totalBoxes);
      const [totalCompartmentsResult] = await pool.execute(queries.totalCompartments);
      const [occupiedCompartmentsResult] = await pool.execute(queries.occupiedCompartments);
      
      // Execute queries that need date parameters
      const [transactionsResult] = await pool.execute(queries.transactionsInPeriod, [startDate, endDate]);
      const [additionsResult] = await pool.execute(queries.additionsInPeriod, [startDate, endDate]);
      const [retrievalsResult] = await pool.execute(queries.retrievalsInPeriod, [startDate, endDate]);

      results.totalItems = totalItemsResult[0].count;
      results.totalBoxes = totalBoxesResult[0].count;
      results.totalCompartments = totalCompartmentsResult[0].count;
      results.occupiedCompartments = occupiedCompartmentsResult[0].count;
      results.availableCompartments = results.totalCompartments - results.occupiedCompartments;
      results.overallUtilization = results.totalCompartments > 0 
        ? ((results.occupiedCompartments / results.totalCompartments) * 100).toFixed(2) + '%'
        : '0%';
      results.transactionsInPeriod = transactionsResult[0].count;
      results.additionsInPeriod = additionsResult[0].count;
      results.retrievalsInPeriod = retrievalsResult[0].count;

      return results;
    } catch (error) {
      throw new Error(`Error fetching system summary: ${error.message}`);
    }
  }

  static async getHourlyActivityDistribution(startDate, endDate) {
    try {
      const query = `
        SELECT 
          HOUR(time) as hour,
          COUNT(*) as total_transactions,
          COUNT(CASE WHEN action = 'added' THEN 1 END) as additions,
          COUNT(CASE WHEN action = 'retrieved' THEN 1 END) as retrievals
        FROM Transactions
        WHERE time BETWEEN ? AND ?
        GROUP BY HOUR(time)
        ORDER BY hour
      `;
      
      const [rows] = await pool.execute(query, [startDate, endDate]);
      
      // Fill in missing hours with 0 values
      const hourlyData = [];
      for (let hour = 0; hour < 24; hour++) {
        const existingData = rows.find(row => row.hour === hour);
        hourlyData.push({
          hour: hour,
          total_transactions: existingData ? existingData.total_transactions : 0,
          additions: existingData ? existingData.additions : 0,
          retrievals: existingData ? existingData.retrievals : 0
        });
      }
      
      return hourlyData;
    } catch (error) {
      throw new Error(`Error fetching hourly activity distribution: ${error.message}`);
    }
  }
}

module.exports = ReportQueries;
