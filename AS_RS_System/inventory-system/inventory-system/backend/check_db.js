const mysql = require('mysql2/promise');

async function checkDatabase() {
    let connection;
    try {
        connection = await mysql.createConnection({
            host: 'localhost',
            user: 'root',
            password: 'aryan@mysql1100',
            database: 'fsm'
        });

        console.log('Checking occupied compartments by item:');
        const [results] = await connection.execute('SELECT item_id, COUNT(*) as count FROM SubCompartments WHERE status = "Occupied" GROUP BY item_id');
        
        results.forEach(row => {
            console.log(`Item ${row.item_id}: ${row.count} occupied compartments`);
        });

        console.log('\nTotal compartments by status:');
        const [statusCounts] = await connection.execute('SELECT status, COUNT(*) as count FROM SubCompartments GROUP BY status');
        statusCounts.forEach(row => {
            console.log(`${row.status}: ${row.count} compartments`);
        });

    } catch (error) {
        console.error('Error checking database:', error);
    } finally {
        if (connection) {
            await connection.end();
        }
    }
}

checkDatabase();
