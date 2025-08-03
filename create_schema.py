import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

# Connect to database
conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD')
)

cur = conn.cursor()

# Create all tables
schema = '''
-- 1. Lead tracking table
CREATE TABLE IF NOT EXISTS leads (
    lead_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    company_name VARCHAR(255),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    icp_score INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 2. Campaign performance table  
CREATE TABLE IF NOT EXISTS campaign_performance (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    campaign_angle VARCHAR(50) NOT NULL,
    emails_sent INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 3. Workflow schedule table
CREATE TABLE IF NOT EXISTS workflow_schedule (
    date DATE PRIMARY KEY,
    workflows_to_run INTEGER NOT NULL,
    leads_per_workflow INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
'''

cur.execute(schema)
conn.commit()
print('✅ Database tables created successfully!')

cur.close()
conn.close()
