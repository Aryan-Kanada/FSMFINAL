const mysql = require('mysql2/promise');
require('dotenv').config();

async function testConnection() {
    let connection;
    try {
        console.log('Testing database connection with env variables...');
        console.log('DB_HOST:', process.env.DB_HOST);
        console.log('DB_USER:', process.env.DB_USER);
        console.log('DB_PASSWORD length:', process.env.DB_PASSWORD?.length);
        console.log('DB_PASSWORD (masked):', process.env.DB_PASSWORD ? '***' + process.env.DB_PASSWORD.slice(-3) : 'undefined');
        console.log('DB_NAME:', process.env.DB_NAME);
        console.log('DB_PORT:', process.env.DB_PORT);
        
        connection = await mysql.createConnection({
            host: process.env.DB_HOST || 'localhost',
            user: process.env.DB_USER || 'root',
            password: process.env.DB_PASSWORD || 'qwertyuiop[]\\',
            database: process.env.DB_NAME || 'inventory_management',
            port: process.env.DB_PORT || 3306
        });

        console.log('✅ Database connection successful!');
        
        // Test a simple query
        const [rows] = await connection.execute('SELECT COUNT(*) as count FROM Boxes');
        console.log(`✅ Query test successful! Found ${rows[0].count} boxes in database`);
        
    } catch (error) {
        console.error('❌ Database connection failed:');
        console.error('Error code:', error.code);
        console.error('Error message:', error.message);
        console.error('SQL State:', error.sqlState);
    } finally {
        if (connection) {
            await connection.end();
        }
    }
}

testConnection();
