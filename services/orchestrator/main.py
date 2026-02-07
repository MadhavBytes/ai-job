"""
Orchestrator Service - Workflow and State Machine Management
Handles the orchestration of all microservices without AI decision-making.
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum

app = FastAPI(title="Job Application Orchestrator")
logger = logging.getLogger(__name__)


class WorkflowState(str, Enum):
    """Workflow states"""
    IDLE = "idle"
    FETCHING_JOBS = "fetching_jobs"
    MATCHING = "matching"
    RESUME_GENERATION = "resume_generation"
    APPLYING = "applying"
    NOTIFYING = "notifying"
    COMPLETED = "completed"
    FAILED = "failed"


class WorkflowManager:
    """Manages application workflow state machine"""
    
    def __init__(self):
        self.workflows: Dict[str, Dict[str, Any]] = {}
    
    def create_workflow(self, user_id: str, preferences: Dict[str, Any]) -> str:
        """Create new workflow"""
        workflow_id = f"wf_{user_id}_{datetime.now().timestamp()}"
        self.workflows[workflow_id] = {
            "id": workflow_id,
            "user_id": user_id,
            "state": WorkflowState.IDLE,
            "preferences": preferences,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "results": {}
        }
        logger.info(f"Created workflow: {workflow_id}")
        return workflow_id
    
    def update_state(self, workflow_id: str, new_state: WorkflowState) -> bool:
        """Update workflow state"""
        if workflow_id not in self.workflows:
            return False
        
        self.workflows[workflow_id]["state"] = new_state
        self.workflows[workflow_id]["updated_at"] = datetime.now()
        logger.info(f"Workflow {workflow_id} state: {new_state}")
        return True
    
    def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow details"""
        return self.workflows.get(workflow_id)


workflow_manager = WorkflowManager()


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/workflows")
async def create_workflow(user_id: str, preferences: Dict[str, Any]):
    """Create new application workflow"""
    try:
        workflow_id = workflow_manager.create_workflow(user_id, preferences)
        return {"workflow_id": workflow_id, "status": "created"}
    except Exception as e:
        logger.error(f"Error creating workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    """Get workflow status"""
    workflow = workflow_manager.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow


@app.post("/workflows/{workflow_id}/start")
async def start_workflow(workflow_id: str):
    """Start workflow execution"""
    if not workflow_manager.update_state(workflow_id, WorkflowState.FETCHING_JOBS):
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"status": "started", "current_state": WorkflowState.FETCHING_JOBS}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
