import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Test Apollo API connection
api_key = os.getenv('APOLLO_API_KEY')

if not api_key:
    print("❌ No Apollo API key found in .env file")
    exit()

headers = {
    "X-Api-Key": api_key,
    "Content-Type": "application/json"
}

# Simple search for 1 person to test
payload = {
    "q_keywords": "owner founder ceo",
    "person_locations": ["United States"],
    "per_page": 1,
    "page": 1
}

try:
    response = requests.post(
        "https://api.apollo.io/v1/mixed_people/search",
        headers=headers,
        json=payload
    )
    
    if response.status_code == 200:
        data = response.json()
        people = data.get("people", [])
        if people:
            person = people[0]
            print("✅ Apollo API working!")
            print(f"Found: {person.get('first_name')} {person.get('last_name')}")
            print(f"Title: {person.get('title')}")
            print(f"Company: {person.get('organization_name')}")
        else:
            print("⚠️ API works but no results found")
    else:
        print(f"❌ API Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Connection failed: {e}")
