const db = require('../config/db');

class BoxModel {
  static async getBoxesWithEmptyCompartments() {
    try {
      const [rows] = await db.query(`
        SELECT DISTINCT b.*
        FROM Boxes b
        JOIN SubCompartments sc ON b.box_id = sc.box_id
        WHERE sc.status = 'Empty'
        UNION
        SELECT b.*
        FROM Boxes b
        LEFT JOIN SubCompartments sc ON b.box_id = sc.box_id
        WHERE sc.subcom_place IS NULL
      `);
      return rows;
    } catch (error) {
      throw new Error(`Error fetching boxes with empty compartments: ${error.message}`);
    }
  }

  static async getAllBoxes() {
    try {
      const [rows] = await db.query('SELECT * FROM Boxes');
      return rows;
    } catch (error) {
      throw new Error(`Error fetching boxes: ${error.message}`);
    }
  }

  static async getBoxById(boxId) {
    try {
      const [rows] = await db.query('SELECT * FROM Boxes WHERE box_id = ?', [boxId]);
      return rows[0];
    } catch (error) {
      throw new Error(`Error fetching box by ID: ${error.message}`);
    }
  }

  static async createBox(boxId, columnName, rowNumber) {
    try {
      const [result] = await db.query(
        'INSERT INTO Boxes (box_id, column_name, `row_number`) VALUES (?, ?, ?)',
        [boxId, columnName, rowNumber]
      );
      return { id: boxId, columnName, rowNumber };
    } catch (error) {
      throw new Error(`Error creating box: ${error.message}`);
    }
  }

  static async deleteBox(boxId) {
    try {
      const [result] = await db.query('DELETE FROM Boxes WHERE box_id = ?', [boxId]);
      return { affectedRows: result.affectedRows };
    } catch (error) {
      throw new Error(`Error deleting box: ${error.message}`);
    }
  }
}

module.exports = BoxModel;
