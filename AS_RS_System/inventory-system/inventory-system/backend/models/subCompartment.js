const db = require('../config/db');

class SubCompartmentModel {
  static async getAllSubCompartments() {
    try {
      const [rows] = await db.query('SELECT * FROM SubCompartments');
      return rows;
    } catch (error) {
      throw new Error(`Error fetching subcompartments: ${error.message}`);
    }
  }

  static async getSubCompartmentByPlace(place) {
    try {
      const [rows] = await db.query('SELECT * FROM SubCompartments WHERE subcom_place = ?', [place]);
      return rows[0];
    } catch (error) {
      throw new Error(`Error fetching subcompartment by place: ${error.message}`);
    }
  }

  static async createSubCompartment(subcomPlace, boxId, subId, itemId, status) {
    try {
      // If itemId is null and status is 'Occupied', this is invalid
      if (!itemId && status === 'Occupied') {
        throw new Error('Item ID is required for Occupied status');
      }

      const [result] = await db.query(
        'INSERT INTO SubCompartments (subcom_place, box_id, sub_id, item_id, status) VALUES (?, ?, ?, ?, ?)',
        [subcomPlace, boxId, subId, itemId, status]
      );
      
      return { 
        subcom_place: subcomPlace, 
        box_id: boxId, 
        sub_id: subId, 
        item_id: itemId, 
        status 
      };
    } catch (error) {
      throw new Error(`Error creating subcompartment: ${error.message}`);
    }
  }

  static async updateStatus(subcomPlace, status, itemId = null) {
    try {
      const [result] = await db.query(
        'UPDATE SubCompartments SET status = ?, item_id = ? WHERE subcom_place = ?',
        [status, itemId, subcomPlace]
      );
      
      return { 
        affectedRows: result.affectedRows,
        subcom_place: subcomPlace,
        status,
        item_id: itemId
      };
    } catch (error) {
      throw new Error(`Error updating subcompartment status: ${error.message}`);
    }
  }

  static async deleteSubCompartment(subcomPlace) {
    try {
      const [result] = await db.query('DELETE FROM SubCompartments WHERE subcom_place = ?', [subcomPlace]);
      return { affectedRows: result.affectedRows };
    } catch (error) {
      throw new Error(`Error deleting subcompartment: ${error.message}`);
    }
  }

  static async addProduct(boxId, subId, itemId) {
    const subcomPlace = `${boxId}${subId}`;
    
    try {
      // Start a transaction
      await db.query('START TRANSACTION');
      
      // Check if place exists
      const [existingPlaces] = await db.query(
        'SELECT status FROM SubCompartments WHERE subcom_place = ?',
        [subcomPlace]
      );
      
      let result;
      
      if (existingPlaces.length > 0) {
        const currentStatus = existingPlaces[0].status;
        
        if (currentStatus === 'Occupied') {
          await db.query('ROLLBACK');
          throw new Error(`SubCompartment ${subcomPlace} is already OCCUPIED`);
        } else {
          // Update the empty place to occupied
          const [updateResult] = await db.query(
            'UPDATE SubCompartments SET item_id = ?, status = ? WHERE subcom_place = ?',
            [itemId, 'Occupied', subcomPlace]
          );
          result = { 
            subcom_place: subcomPlace,
            action: 'updated',
            status: 'Occupied',
            item_id: itemId
          };
        }
      } else {
        // Create new subcompartment
        const [createResult] = await db.query(
          'INSERT INTO SubCompartments (subcom_place, box_id, sub_id, item_id, status) VALUES (?, ?, ?, ?, ?)',
          [subcomPlace, boxId, subId, itemId, 'Occupied']
        );
        result = { 
          subcom_place: subcomPlace,
          action: 'created',
          status: 'Occupied',
          item_id: itemId
        };
      }
      
      // Record transaction
      const [transactionResult] = await db.query(
        'INSERT INTO Transactions (item_id, subcom_place, action, time) VALUES (?, ?, ?, NOW())',
        [itemId, subcomPlace, 'added']
      );
      
      // Commit the transaction
      await db.query('COMMIT');
      
      return { 
        ...result, 
        transaction_id: transactionResult.insertId
      };
    } catch (error) {
      // Rollback in case of error
      await db.query('ROLLBACK');
      throw new Error(`Error adding product: ${error.message}`);
    }
  }

  static async retrieveProduct(itemId, quantity) {
    try {
      // Start a transaction
      await db.query('START TRANSACTION');
      
      // Get occupied products with column-wise priority
      const [availableItems] = await db.query(`
        SELECT sc.subcom_place, sc.box_id, sc.sub_id, sc.item_id, sc.status,
               b.column_name, b.\`row_number\`
        FROM SubCompartments sc
        JOIN Boxes b ON sc.box_id = b.box_id
        WHERE sc.item_id = ? AND sc.status = 'Occupied'
        ORDER BY b.column_name, b.\`row_number\`, sc.sub_id
        LIMIT ?
      `, [itemId, quantity]);
      
      if (availableItems.length < quantity) {
        await db.query('ROLLBACK');
        throw new Error(`Only ${availableItems.length} items available, but ${quantity} requested`);
      }
      
      const retrievedLocations = [];
      
      // Update status to 'Empty' for retrieved items
      for (const item of availableItems) {
        const subcomPlace = item.subcom_place;
        
        // Update to empty
        await db.query(
          'UPDATE SubCompartments SET status = ?, item_id = NULL WHERE subcom_place = ?',
          ['Empty', subcomPlace]
        );
        
        // Record transaction
        const [transResult] = await db.query(
          'INSERT INTO Transactions (item_id, subcom_place, action, time) VALUES (?, ?, ?, NOW())',
          [itemId, subcomPlace, 'retrieved']
        );
        
        retrievedLocations.push({
          subcom_place: subcomPlace,
          column_name: item.column_name,
          row_number: item.row_number,
          sub_id: item.sub_id,
          transaction_id: transResult.insertId
        });
      }
      
      // Commit transaction
      await db.query('COMMIT');
      
      return {
        item_id: itemId,
        quantity: retrievedLocations.length,
        locations: retrievedLocations
      };
      
    } catch (error) {
      // Rollback in case of error
      await db.query('ROLLBACK');
      throw new Error(`Error retrieving product: ${error.message}`);
    }
  }
}

module.exports = SubCompartmentModel;
