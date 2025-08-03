#!/usr/bin/env python3
"""
On Pulse Solutions - Database Deployment Script
Python version for deploying the complete outreach database schema
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv
from pathlib import Path
import sys
from getpass import getpass

# Color output for Windows/Unix
class Colors:
    GREEN = '\033[92m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.ENDC}")

def print_info(msg):
    print(f"{Colors.CYAN}{msg}{Colors.ENDC}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.ENDC}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.ENDC}")

def main():
    # Banner
    print_info("\n" + "="*60)
    print_info("     On Pulse Solutions - Database Deployment")
    print_info("            Outreach System Schema v1.0")
    print_info("="*60 + "\n")

    # Load environment variables
    load_dotenv()
    
    # Configuration
    config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'onpulse_outreach'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', '')
    }
    
    # Display connection info
    print_info("Database Connection:")
    print(f"  Host:     {config['host']}:{config['port']}")
    print(f"  Database: {config['database']}")
    print(f"  User:     {config['user']}")
    
    # Get password if not in env
    if not config['password']:
        config['password'] = getpass('\nEnter database password: ')
    
    # Test connection
    print_info("\nTesting database connection...")
    try:
        # First, try to connect to the database
        conn = psycopg2.connect(**config)
        conn.close()
        print_success("Connection successful!")
        
    except psycopg2.OperationalError as e:
        if "does not exist" in str(e):
            print_warning(f"Database '{config['database']}' does not exist")
            
            # Offer to create it
            create_db = input("\nWould you like to create it? (y/n): ").lower()
            if create_db == 'y':
                # Connect to postgres database to create the new one
                print_info("Creating database...")
                try:
                    temp_config = config.copy()
                    temp_config['database'] = 'postgres'
                    conn = psycopg2.connect(**temp_config)
                    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
                    cur = conn.cursor()
                    cur.execute(f"CREATE DATABASE {config['database']}")
                    cur.close()
                    conn.close()
                    print_success(f"Database '{config['database']}' created!")
                except Exception as create_error:
                    print_error(f"Failed to create database: {create_error}")
                    return 1
            else:
                print_error("Cannot proceed without database")
                return 1
        else:
            print_error(f"Connection failed: {e}")
            print_warning("\nTroubleshooting tips:")
            print("  1. Check password is correct")
            print("  2. Verify PostgreSQL is running")
            print("  3. Check host and port are correct")
            print("  4. Ensure user has proper permissions")
            return 1
    
    # Check for schema file
    schema_file = Path('database/complete_schema.sql')
    if not schema_file.exists():
        print_warning("\nSchema file not found at database/complete_schema.sql")
        
        # Check if the artifact content should be saved
        print_info("\nTo deploy the schema:")
        print("  1. Create directory: mkdir database")
        print("  2. Save the schema artifact content to: database/complete_schema.sql")
        print("  3. Run this script again")
        
        # Offer to create directory
        if not Path('database').exists():
            create_dir = input("\nCreate 'database' directory now? (y/n): ").lower()
            if create_dir == 'y':
                Path('database').mkdir(exist_ok=True)
                print_success("Directory created!")
                print("\nNow save the schema artifact to: database/complete_schema.sql")
        return 1
    
    # Deploy schema
    print_info("\n" + "="*60)
    print_info("Starting database deployment...")
    print_info("="*60)
    
    try:
        conn = psycopg2.connect(**config)
        cur = conn.cursor()
        
        # Read and execute schema
        print_info("\nExecuting schema file...")
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
        
        # Execute the entire schema
        cur.execute(schema_sql)
        conn.commit()
        
        print_success("Schema deployed successfully!")
        
        # Verify tables
        print_info("\nVerifying tables...")
        cur.execute("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public' 
            ORDER BY tablename
        """)
        tables = cur.fetchall()
        
        if tables:
            print_success(f"Created {len(tables)} tables:")
            for table in tables:
                print(f"  - {table[0]}")
        
        # Verify views
        print_info("\nVerifying views...")
        cur.execute("""
            SELECT viewname FROM pg_views 
            WHERE schemaname = 'public' 
            ORDER BY viewname
        """)
        views = cur.fetchall()
        
        if views:
            print_success(f"Created {len(views)} views:")
            for view in views:
                print(f"  - {view[0]}")
        
        # Verify functions
        print_info("\nVerifying functions...")
        cur.execute("""
            SELECT routine_name FROM information_schema.routines 
            WHERE routine_schema = 'public' 
            AND routine_type = 'FUNCTION'
            ORDER BY routine_name
        """)
        functions = cur.fetchall()
        
        if functions:
            print_success(f"Created {len(functions)} functions:")
            for func in functions:
                print(f"  - {func[0]}")
        
        # Summary
        print_info("\n" + "="*60)
        print_success("DEPLOYMENT COMPLETE!")
        print_info("="*60)
        
        print("\n" + Colors.BOLD + "Next steps:" + Colors.ENDC)
        print("  1. Run test queries to verify schema")
        print("  2. Configure initial workflow schedule")
        print("  3. Load baseline playbooks")
        print("  4. Test API connections")
        
        # Offer to run tests
        run_tests = input("\nRun verification tests? (y/n): ").lower()
        if run_tests == 'y':
            print_info("\nRunning verification tests...")
            
            # Test 1: Insert a lead
            try:
                cur.execute("""
                    INSERT INTO leads (email, first_name, last_name, company_name) 
                    VALUES ('test@example.com', 'Test', 'User', 'Test Co') 
                    ON CONFLICT (email) DO NOTHING 
                    RETURNING lead_id
                """)
                result = cur.fetchone()
                if result:
                    print_success("Lead insertion test passed")
                conn.commit()
            except Exception as e:
                print_warning(f"Lead insertion test failed: {e}")
                conn.rollback()
            
            # Test 2: Check campaign weights
            try:
                cur.execute("""
                    SELECT campaign_angle, current_weight 
                    FROM thompson_sampling_weights 
                    WHERE date = CURRENT_DATE
                """)
                weights = cur.fetchall()
                if weights:
                    print_success(f"Campaign weights initialized: {len(weights)} campaigns")
                    for angle, weight in weights:
                        print(f"  - {angle}: {weight}")
            except Exception as e:
                print_warning(f"Campaign weights test failed: {e}")
            
            # Test 3: Check workflow schedule
            try:
                cur.execute("""
                    SELECT COUNT(*) FROM workflow_schedule 
                    WHERE date = CURRENT_DATE
                """)
                count = cur.fetchone()[0]
                print_success(f"Workflow schedule check passed (entries today: {count})")
            except Exception as e:
                print_warning(f"Workflow schedule test failed: {e}")
            
            # Cleanup test data
            print_info("\nCleaning up test data...")
            cur.execute("DELETE FROM leads WHERE email = 'test@example.com'")
            conn.commit()
        
        cur.close()
        conn.close()
        
        print_success("\n✓ All done!")
        return 0
        
    except Exception as e:
        print_error(f"\nDeployment failed: {e}")
        print_warning("\nThe error above may indicate:")
        print("  - Syntax error in schema file")
        print("  - Permission issues")
        print("  - Existing tables conflicting")
        
        # Offer to drop and recreate
        if "already exists" in str(e):
            print_warning("\nSome tables already exist.")
            drop = input("Drop all tables and start fresh? (y/n): ").lower()
            if drop == 'y':
                try:
                    conn = psycopg2.connect(**config)
                    cur = conn.cursor()
                    
                    # Drop all tables CASCADE
                    cur.execute("""
                        DROP SCHEMA public CASCADE;
                        CREATE SCHEMA public;
                        GRANT ALL ON SCHEMA public TO postgres;
                        GRANT ALL ON SCHEMA public TO public;
                    """)
                    conn.commit()
                    cur.close()
                    conn.close()
                    
                    print_success("Schema reset complete!")
                    print("Run the script again to deploy fresh schema.")
                    
                except Exception as drop_error:
                    print_error(f"Failed to reset schema: {drop_error}")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())