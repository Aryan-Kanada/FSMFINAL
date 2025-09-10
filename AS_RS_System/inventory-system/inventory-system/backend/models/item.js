const db = require('../config/db');

class ItemModel {
  static async getAllItems() {
    try {
      const [rows] = await db.query('SELECT * FROM Items');
      return rows;
    } catch (error) {
      throw new Error(`Error fetching items: ${error.message}`);
    }
  }

  static async getItemById(itemId) {
    try {
      const [rows] = await db.query('SELECT * FROM Items WHERE item_id = ?', [itemId]);
      return rows[0];
    } catch (error) {
      throw new Error(`Error fetching item by ID: ${error.message}`);
    }
  }

  static async createItem(itemId, name, description) {
    try {
      const [result] = await db.query(
        'INSERT INTO Items (item_id, name, description, added_on) VALUES (?, ?, ?, NOW())',
        [itemId, name, description]
      );
      
      // Fetch the newly created item to return complete data
      const [items] = await db.query('SELECT * FROM Items WHERE item_id = ?', [itemId]);
      return items[0];
    } catch (error) {
      throw new Error(`Error creating item: ${error.message}`);
    }
  }

  static async deleteItem(itemId) {
    try {
      const [result] = await db.query('DELETE FROM Items WHERE item_id = ?', [itemId]);
      return { affectedRows: result.affectedRows };
    } catch (error) {
      throw new Error(`Error deleting item: ${error.message}`);
    }
  }

  static async getAvailableItemsWithCount() {
    try {
      const [rows] = await db.query(`
        SELECT i.item_id, i.name, COUNT(*) as available_count
        FROM Items i
        JOIN SubCompartments sc ON i.item_id = sc.item_id
        WHERE sc.status = 'Occupied'
        GROUP BY i.item_id, i.name
        ORDER BY i.name
      `);
      return rows;
    } catch (error) {
      throw new Error(`Error fetching available items: ${error.message}`);
    }
  }

  static async getItemLocations(itemId) {
    try {
      const [rows] = await db.query(`
        SELECT sc.subcom_place, b.column_name, b.\`row_number\`, sc.sub_id
        FROM SubCompartments sc
        JOIN Boxes b ON sc.box_id = b.box_id
        WHERE sc.item_id = ? AND sc.status = 'Occupied'
      `, [itemId]);
      return rows;
    } catch (error) {
      throw new Error(`Error fetching item locations: ${error.message}`);
    }
  }

  static async checkItemIdExists(itemId) {
    try {
      const [rows] = await db.query('SELECT COUNT(*) as count FROM Items WHERE item_id = ?', [itemId]);
      return rows[0].count > 0;
    } catch (error) {
      throw new Error(`Error checking item ID: ${error.message}`);
    }
  }
}

module.exports = ItemModel;
