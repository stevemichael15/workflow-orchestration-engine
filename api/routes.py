from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from engine.executor import execute_workflow
from db.connection import get_connection

router = APIRouter()

class ExecuteWorkflowRequest(BaseModel):
    template_id: str
    inputs: Dict[str, Any]


class AppealRequest(BaseModel):
    original_instance_id: str
    new_data: Dict[str, Any]
    

@router.post("/workflows/execute")
def run_workflow(request: ExecuteWorkflowRequest):
    try:
        instance_id = execute_workflow(
            template_id=request.template_id,
            inputs=request.inputs
        )
        return {
            "instance_id": instance_id,
            "status": "started"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
      
@router.get("/workflows/{instance_id}")
def get_workflow(instance_id: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT status, outputs, triggered_at
        FROM workflow_instances
        WHERE instance_id = %s
        """,
        (instance_id,)
    )

    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Workflow not found")

    status, outputs, triggered_at = row

    return {
        "instance_id": instance_id,
        "status": status,
        "outputs": outputs,
        "triggered_at": triggered_at
    }
    
@router.get("/workflows/{instance_id}/audit")
def get_audit(instance_id: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT step_name, started_at, completed_at,
               status, input_snapshot, output_snapshot, error_message
        FROM audit_trail
        WHERE instance_id = %s
        ORDER BY id
        """,
        (instance_id,)
    )

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {
            "step_name": r[0],
            "started_at": r[1],
            "completed_at": r[2],
            "status": r[3],
            "input": r[4],
            "output": r[5],
            "error": r[6]
        }
        for r in rows
    ]
    
@router.post("/workflows/appeal")
def submit_appeal(request: AppealRequest):
    # Create new workflow instance using eligibility_check template
    new_instance_id = execute_workflow(
        template_id="eligibility_check",
        inputs={
            "citizen_id": request.original_instance_id,
            **request.new_data
        }
    )

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO appeals (appeal_of, new_instance_id, outcome)
        VALUES (%s, %s, %s)
        """,
        (request.original_instance_id, new_instance_id, "pending")
    )

    conn.commit()
    cur.close()
    conn.close()

    return {
        "new_instance_id": new_instance_id,
        "status": "appeal_submitted"
    }
    
@router.get("/workflows/report/{instance_id}")
def get_report(instance_id: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT outputs
        FROM workflow_instances
        WHERE instance_id = %s
        """,
        (instance_id,)
    )

    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Workflow not found")

    return row[0]