import mysql.connector
import subprocess
import sys
import os

def setup_database():
    print("Setting up MySQL database...")
    # Try to import and setup the database with SQL file
    try:
        # First try to run the SQL file directly
        mysql_cmd = 'mysql -u root -e "CREATE DATABASE IF NOT EXISTS inventory_management;"'
        result = subprocess.run(mysql_cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Database created successfully")
            # Import the SQL file
            import_cmd = 'mysql -u root inventory_management < inventory_management.sql'
            result2 = subprocess.run(import_cmd, shell=True, capture_output=True, text=True)
            if result2.returncode == 0:
                print("✅ Database tables imported successfully")
                return True
            else:
                print("⚠️ Database exists but may need manual SQL import")
                print("Run: mysql -u root inventory_management < inventory_management.sql")
        # Try with mysql.connector
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password=''
        )
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS inventory_management")
        cursor.execute("USE inventory_management")
        # Check if tables exist
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        if not tables:
            print("⚠️ Database created but no tables found")
            print("Please run: mysql -u root inventory_management < inventory_management.sql")
        else:
            print(f"✅ Found {len(tables)} tables in database")
        conn.close()
        return True
    except mysql.connector.Error as e:
        if "Access denied" in str(e):
            print("❌ MySQL Access denied - Please ensure MySQL is running")
            print("Try: mysqld --skip-grant-tables --skip-networking")
            print("Or install/start MySQL service")
        else:
            print(f"❌ MySQL error: {e}")
        return False
    except Exception as e:
        print(f"❌ Setup error: {e}")
        return False

if __name__ == "__main__":
    setup_database()
