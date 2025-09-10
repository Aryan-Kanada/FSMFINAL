// Fix database script
const db = require('./backend/config/db');

async function fixDatabase() {
    try {
        console.log('Starting database fix...');
        
        // Fix all 'Free' status to 'Empty' where item_id is NULL
        const [result] = await db.query(`
            UPDATE SubCompartments 
            SET status = 'Empty' 
            WHERE status = 'Free' AND item_id IS NULL
        `);
        
        console.log(`Fixed ${result.affectedRows} corrupted records`);
        
        // Show status counts
        const [statusCount] = await db.query(`
            SELECT status, COUNT(*) as count 
            FROM SubCompartments 
            GROUP BY status
        `);
        
        console.log('Current status distribution:');
        statusCount.forEach(row => {
            console.log(`  ${row.status}: ${row.count}`);
        });
        
        // Show corrected inventory
        const [inventory] = await db.query(`
            SELECT 
                i.item_id,
                i.name,
                COUNT(sc.subcom_place) as available_count
            FROM Items i
            LEFT JOIN SubCompartments sc ON i.item_id = sc.item_id AND sc.status = 'Occupied'
            GROUP BY i.item_id, i.name
            ORDER BY i.item_id
        `);
        
        console.log('Corrected inventory counts:');
        inventory.forEach(item => {
            console.log(`  ${item.name}: ${item.available_count}`);
        });
        
        console.log('Database fix completed successfully!');
        
    } catch (error) {
        console.error('Database fix failed:', error);
    }
    
    process.exit(0);
}

fixDatabase();
