from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime
import uuid
from langgraph.graph import StateGraph, END
from loguru import logger
import asyncio

class WorkflowState(TypedDict):
    """State management for the workflow"""
    # Batch info
    workflow_run_id: str
    batch_number: int
    timestamp: datetime
    
    # Lead data
    leads: List[Dict[str, Any]]
    enriched_leads: List[Dict[str, Any]]
    qualified_leads: List[Dict[str, Any]]
    
    # Processing state
    current_step: str
    errors: List[Dict[str, Any]]
    metrics: Dict[str, Any]

class OutreachWorkflow:
    """Main workflow orchestrator"""
    
    def __init__(self):
        self.workflow = self._build_workflow()
        logger.info("Outreach workflow initialized")
    
    def _build_workflow(self) -> StateGraph:
        """Build the workflow graph"""
        workflow = StateGraph(WorkflowState)
        
        # Add nodes (each agent is a node)
        workflow.add_node("source_leads", self.source_leads)
        workflow.add_node("enrich_leads", self.enrich_leads)
        workflow.add_node("score_leads", self.score_leads)
        workflow.add_node("persist_state", self.persist_state)
        
        # Define the flow
        workflow.set_entry_point("source_leads")
        workflow.add_edge("source_leads", "enrich_leads")
        workflow.add_edge("enrich_leads", "score_leads")
        workflow.add_edge("score_leads", "persist_state")
        workflow.add_edge("persist_state", END)
        
        return workflow.compile()
    
    def source_leads(self, state: WorkflowState) -> WorkflowState:
        """Source leads from Apollo"""
        logger.info(f"Sourcing leads for batch {state['batch_number']}")
        state['current_step'] = 'sourcing'
        
        # For now, use dummy data
        state['leads'] = [
            {
                "email": f"owner{i}@company{i}.com",
                "company_name": f"Test Company {i}",
                "first_name": f"John{i}",
                "last_name": "Smith"
            }
            for i in range(1, 4)
        ]
        logger.info(f"Sourced {len(state['leads'])} leads")
        return state
    
    def enrich_leads(self, state: WorkflowState) -> WorkflowState:
        """Enrich lead data"""
        logger.info("Enriching leads")
        state['current_step'] = 'enriching'
        
        # Simple enrichment for testing
        state['enriched_leads'] = []
        for lead in state['leads']:
            enriched = lead.copy()
            enriched['revenue'] = 5000000
            enriched['employees'] = 50
            state['enriched_leads'].append(enriched)
        
        logger.info(f"Enriched {len(state['enriched_leads'])} leads")
        return state
    
    def score_leads(self, state: WorkflowState) -> WorkflowState:
        """Score leads with ICP criteria"""
        logger.info("Scoring leads")
        state['current_step'] = 'scoring'
        
        state['qualified_leads'] = []
        for lead in state['enriched_leads']:
            lead['icp_score'] = 75  # Dummy score
            if lead['icp_score'] >= 60:
                state['qualified_leads'].append(lead)
        
        logger.info(f"Qualified {len(state['qualified_leads'])} leads")
        return state
    
    def persist_state(self, state: WorkflowState) -> WorkflowState:
        """Save to database"""
        logger.info("Persisting state to database")
        state['current_step'] = 'complete'
        
        # We'll add actual database saving next
        logger.info("Workflow complete!")
        return state
    
    def run(self, batch_number: int = 1) -> WorkflowState:
        """Run the workflow for a batch"""
        initial_state = WorkflowState(
            workflow_run_id=str(uuid.uuid4()),
            batch_number=batch_number,
            timestamp=datetime.now(),
            leads=[],
            enriched_leads=[],
            qualified_leads=[],
            current_step="starting",
            errors=[],
            metrics={}
        )
        
        logger.info(f"Starting workflow run {initial_state['workflow_run_id']}")
        result = self.workflow.invoke(initial_state)
        return result

if __name__ == "__main__":
    workflow = OutreachWorkflow()
    result = workflow.run(batch_number=1)
    print(f"\n✅ Workflow completed!")
    print(f"Run ID: {result['workflow_run_id']}")
    print(f"Qualified leads: {len(result['qualified_leads'])}")
