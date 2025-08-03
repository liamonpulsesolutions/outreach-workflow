import os
import requests
import time
from typing import Dict, List, Any
from loguru import logger
from dotenv import load_dotenv
import json

load_dotenv()

class ApolloAgent:
    def __init__(self):
        self.api_key = os.getenv('APOLLO_API_KEY')
        self.base_url = "https://api.apollo.io/v1"
        self.headers = {
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
            "X-Api-Key": self.api_key
        }
        
    def search_people(self, search_params: Dict, limit: int = 10) -> List[Dict]:
        """Search for 10 people using PARAMS in POST (your working format)"""
        url = f"https://api.apollo.io/api/v1/mixed_people/search"  # Note: /api/v1 not just /v1
        
        # Use PARAMS not body (as per your working code)
        params = {
            "q_keywords": search_params.get("q_keywords", "owner founder ceo president"),
            "person_titles[]": search_params.get("person_titles", ["owner", "founder", "ceo", "president"]),
            "person_locations[]": ["United States"],
            "organization_num_employees_ranges[]": ["1,20", "21,50", "51,100"],
            "page": search_params.get("page", 1),
            "per_page": limit
        }
        
        try:
            logger.info(f"Searching Apollo for {limit} people")
            # POST with params, empty body
            response = requests.post(url, headers=self.headers, params=params, json={})
            response.raise_for_status()
            
            data = response.json()
            people = data.get("people", [])
            logger.info(f"Found {len(people)} people")
            
            return people
            
        except Exception as e:
            logger.error(f"Apollo search failed: {e}")
            return []
    
    def enrich_people_bulk(self, people: List[Dict]) -> List[Dict]:
        """Bulk enrich using BODY with details array (your working format)"""
        endpoint = f"{self.base_url}/people/bulk_match"
        
        # Build details array exactly like your working code
        details = []
        for p in people:
            org = p.get("organization") or {}
            domain = org.get("domain", "")
            
            details.append({
                "id": p.get("id"),
                "first_name": p.get("first_name"),
                "last_name": p.get("last_name"),
                "company_domain": domain
            })
        
        payload = {"details": details}
        
        params = {
            "reveal_personal_emails": "true",
            "reveal_phone_number": "false"
        }
        
        try:
            logger.info(f"Enriching {len(details)} people")
            # POST with body AND params
            response = requests.post(endpoint, headers=self.headers, json=payload, params=params)
            response.raise_for_status()
            
            data = response.json()
            matches = data.get("matches", [])
            logger.info(f"Enriched {len(matches)} people successfully")
            
            return matches
            
        except Exception as e:
            logger.error(f"Person enrichment failed: {e}")
            return []
    
    def enrich_organizations(self, domains: List[str]) -> List[Dict]:
        """Bulk enrich orgs using domains[] param format (your working format)"""
        endpoint = f"{self.base_url}/organizations/bulk_enrich"
        
        # Build params with domains[] format exactly like your code
        params = [("domains[]", domain) for domain in domains]
        
        try:
            logger.info(f"Enriching {len(domains)} organizations")
            # POST with params as list of tuples, empty body
            response = requests.post(endpoint, headers=self.headers, params=params, json={})
            response.raise_for_status()
            
            data = response.json()
            orgs = data.get("organizations", [])
            logger.info(f"Enriched {len(orgs)} organizations successfully")
            
            return orgs
            
        except Exception as e:
            logger.error(f"Organization enrichment failed: {e}")
            return []
    
    def process_batch_of_10(self, search_params: Dict) -> Dict:
        """Process a single batch of 10 leads through the full pipeline"""
        results = {
            "raw_people": [],
            "enriched_people": [],
            "valid_emails": [],
            "enriched_orgs": [],
            "qualified_leads": []
        }
        
        # Step 1: Search for 10 people
        people = self.search_people(search_params, limit=10)
        results["raw_people"] = people
        
        if not people:
            logger.warning("No people found in search")
            return results
        
        # Step 2: Enrich people
        enriched = self.enrich_people_bulk(people)
        results["enriched_people"] = enriched
        
        # Step 3: Extract emails for validation (Neverbounce later)
        emails_to_validate = []
        unique_domains = set()
        
        for person in enriched:
            email = person.get("email")
            if email:
                emails_to_validate.append({
                    "email": email,
                    "person_id": person.get("id"),
                    "person": person
                })
                
                # Extract domain for org enrichment
                org = person.get("organization", {})
                domain = org.get("domain")
                if domain:
                    unique_domains.add(domain)
        
        # For now, mark all as valid (Neverbounce next step)
        results["valid_emails"] = emails_to_validate
        logger.info(f"Found {len(emails_to_validate)} emails to validate")
        
        # Step 4: Enrich organizations
        if unique_domains:
            enriched_orgs = self.enrich_organizations(list(unique_domains))
            results["enriched_orgs"] = enriched_orgs
            
            # Index by domain for easy lookup
            org_by_domain = {
                org.get("primary_domain"): org 
                for org in enriched_orgs 
                if org.get("primary_domain")
            }
        else:
            org_by_domain = {}
        
        # Step 5: Combine into qualified leads
        for email_data in results["valid_emails"]:
            person = email_data["person"]
            person_org = person.get("organization", {})
            domain = person_org.get("domain")
            
            # Get enriched org data if available
            enriched_org = org_by_domain.get(domain, {})
            
            qualified_lead = {
                "email": email_data.get("email"),
                "first_name": person.get("first_name"),
                "last_name": person.get("last_name"),
                "title": person.get("title"),
                "company_name": enriched_org.get("name") or person_org.get("name"),
                "company_size": enriched_org.get("estimated_num_employees"),
                "revenue": enriched_org.get("estimated_annual_revenue"),
                "industry": enriched_org.get("industry"),
                "domain": domain,
                "person_data": person,
                "org_data": enriched_org
            }
            results["qualified_leads"].append(qualified_lead)
        
        logger.info(f"Batch complete: {len(results['qualified_leads'])} qualified leads")
        return results
