import mysql.connector
import sys

def setup_database():
    try:
        # Connect to MySQL server (without database)
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password=''
        )
        cursor = conn.cursor()
        
        # Create database if not exists
        cursor.execute("CREATE DATABASE IF NOT EXISTS inventory_management")
        cursor.execute("USE inventory_management")
        
        print("✅ Database inventory_management created/verified")
        
        # Check if tables exist
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        
        if not tables:
            print("❌ No tables found. Please run inventory_management.sql first")
            print("Command: mysql -u root -p inventory_management < inventory_management.sql")
        else:
            print(f"✅ Found {len(tables)} tables: {', '.join(tables)}")
        
        conn.close()
        return True
        
    except mysql.connector.Error as e:
        print(f"❌ Database error: {e}")
        print("Make sure MySQL is running and accessible")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    setup_database()
