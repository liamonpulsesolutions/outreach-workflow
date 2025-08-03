import os
import json
import requests
from typing import List, Dict, Any, Optional
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

class ApolloSearchManager:
    """Modular Apollo search manager with configurable parameters"""
    
    def __init__(self, config_path: str = "config/apollo_search_config.json"):
        self.api_key = os.getenv("APOLLO_API_KEY")
        self.config = self._load_config(config_path)
        self.progress_file = Path("data/apollo_progress.json")
        self.progress_file.parent.mkdir(exist_ok=True)
        
        self.headers = {
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
            "X-Api-Key": self.api_key or "dummy"
        }
        
        logger.info(f"Apollo Search Manager initialized with {len(self.config['us_industries'])} industries")
    
    def _load_config(self, config_path: str) -> dict:
        """Load search configuration"""
        path = Path(config_path)
        if not path.exists():
            logger.error(f"Config file not found: {config_path}")
            return self._default_config()
        
        with open(path, 'r') as f:
            return json.load(f)
    
    def get_search_params(self, 
                         industry: str = None,
                         metro: str = None,
                         strategy: str = "broad",
                         custom_overrides: dict = None) -> dict:
        """Build search parameters from config with optional overrides"""
        
        # Start with base parameters
        base = self.config["base_search_params"].copy()
        
        # Convert to Apollo format
        params = {
            "person_titles[]": base["person_titles"],
            "person_seniorities[]": base["person_seniorities"],
            "contact_email_status[]": base["contact_email_status"],
            "organization_num_employees_ranges[]": base["organization_num_employees_ranges"]
        }
        
        # Add industry keywords
        if industry and industry in self.config["us_industries"]:
            industry_config = self.config["us_industries"][industry]
            params["q_keywords"] = industry_config["keywords"]
        
        # Add location targeting
        if metro and metro in self.config["us_metro_areas"]:
            metro_config = self.config["us_metro_areas"][metro]
            params["person_locations[]"] = metro_config["cities"]
        
        # Apply strategy settings
        if strategy in self.config["search_strategies"]:
            strategy_config = self.config["search_strategies"][strategy]
            params["per_page"] = strategy_config.get("per_page", 10)
            
            # Add any additional filters from strategy
            if "additional_filters" in strategy_config:
                params.update(strategy_config["additional_filters"])
        
        # Apply custom overrides last
        if custom_overrides:
            params.update(custom_overrides)
        
        return params
    
    def update_config(self, updates: dict):
        """Update configuration dynamically"""
        # Deep merge updates into config
        self._deep_merge(self.config, updates)
        
        # Save updated config
        config_path = Path("config/apollo_search_config.json")
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
        
        logger.info("Configuration updated and saved")
    
    def add_industry(self, name: str, keywords: str, priority: int = 3):
        """Add a new industry to search configuration"""
        self.config["us_industries"][name] = {
            "keywords": keywords,
            "priority": priority,
            "target_revenue": ["1M-20M"]
        }
        self.update_config({})  # Trigger save
        logger.info(f"Added industry: {name}")
    
    def get_next_search_params(self) -> tuple[dict, dict]:
        """Get next search parameters with automatic rotation"""
        progress = self._load_progress()
        
        # Get current position in rotation
        industries = sorted(
            self.config["us_industries"].items(),
            key=lambda x: x[1].get("priority", 99)
        )
        metros = list(self.config["us_metro_areas"].keys())
        
        industry_idx = progress.get("industry_index", 0)
        metro_idx = progress.get("metro_index", 0)
        
        industry_name = industries[industry_idx % len(industries)][0]
        metro_name = metros[metro_idx % len(metros)]
        
        # Get page for this combination
        combo_key = f"{industry_name}_{metro_name}"
        page = progress.get("pages", {}).get(combo_key, 0) + 1
        
        # Build parameters
        params = self.get_search_params(
            industry=industry_name,
            metro=metro_name,
            strategy="broad"
        )
        params["page"] = page
        
        # Update progress
        progress["pages"] = progress.get("pages", {})
        progress["pages"][combo_key] = page
        progress["industry_index"] = (industry_idx + 1) % len(industries)
        if industry_idx + 1 >= len(industries):
            progress["metro_index"] = (metro_idx + 1) % len(metros)
        
        self._save_progress(progress)
        
        metadata = {
            "industry": industry_name,
            "metro": metro_name,
            "page": page,
            "strategy": "broad"
        }
        
        return params, metadata
    
    def _load_progress(self) -> dict:
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_progress(self, progress: dict):
        with open(self.progress_file, 'w') as f:
            json.dump(progress, f, indent=2)
    
    def _deep_merge(self, base: dict, updates: dict):
        """Deep merge updates into base dictionary"""
        for key, value in updates.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def _default_config(self) -> dict:
        """Return minimal default config if file not found"""
        return {
            "base_search_params": {
                "person_titles": ["Owner", "CEO", "Founder"],
                "person_seniorities": ["owner", "founder"],
                "contact_email_status": ["verified"],
                "organization_num_employees_ranges": ["1,50"]
            },
            "us_industries": {
                "general": {"keywords": "business", "priority": 1}
            },
            "us_metro_areas": {
                "default": {"cities": ["United States"]}
            },
            "search_strategies": {
                "broad": {"per_page": 10}
            }
        }

if __name__ == "__main__":
    # Test the modular system
    manager = ApolloSearchManager()
    
    # Get next search parameters
    params, metadata = manager.get_next_search_params()
    
    print("\n✅ Modular Apollo Search Configuration")
    print(f"\nNext search:")
    print(f"  Industry: {metadata['industry']}")
    print(f"  Metro: {metadata['metro']}")
    print(f"  Page: {metadata['page']}")
    print(f"\nParameters:")
    for key, value in params.items():
        if isinstance(value, list):
            print(f"  {key}: {len(value)} items")
        else:
            print(f"  {key}: {value}")
    
    # Example: Add a new industry
    manager.add_industry("saas", "software as a service SaaS B2B cloud", priority=2)
