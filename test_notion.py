from notion_client import Client
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# You'll need to add your Notion API key to .env first
# Get it from: https://www.notion.so/my-integrations

notion = Client(auth=os.getenv('NOTION_API_KEY'))

# Database IDs from what we just created
databases = {
    'Daily Performance': '4dab07fdfc8c46fc9e30e93f6fd8b086',
    'Campaign Performance': 'c77f6621c2dd4488be25e914a5bac9dd',
    'Workflow Runs': '1ea62e668e31485487e1f73a16ea0e07',
    'Alert Log': 'dcd5d19ffdc54509a349b70552047403'
}

# Test writing to Alert Log
try:
    response = notion.pages.create(
        parent={'database_id': databases['Alert Log']},
        properties={
            'Alert': {'title': [{'text': {'content': 'Test Connection Successful'}}]},
            'Type': {'select': {'name': 'Success'}},
            'Component': {'select': {'name': 'Database'}},
            'Message': {'rich_text': [{'text': {'content': 'Successfully connected to Notion API from Python'}}]},
            'Resolved': {'checkbox': False}
        }
    )
    print('✅ Notion API connection successful!')
    print(f"Created test entry in Alert Log")
except Exception as e:
    print(f'❌ Error: {e}')
    print('Make sure to add NOTION_API_KEY to your .env file')
