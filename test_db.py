import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

try:
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    
    cur = conn.cursor()
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    tables = cur.fetchall()
    
    print('✅ PostgreSQL Setup Complete!')
    print('\nTables created:')
    for table in tables:
        print(f'  - {table[0]}')
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f'❌ Error: {e}')
