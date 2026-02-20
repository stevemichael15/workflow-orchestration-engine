import json
import uuid
from datetime import datetime

from engine.registry import TASK_REGISTRY
from db.connection import get_connection

def load_template(template_id: str) -> dict:
    path = f"templates/{template_id}.json"
    with open(path, "r") as f:
        return json.load(f)
      
def create_workflow_instance(template_id, inputs):
    instance_id = str(uuid.uuid4())

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO workflow_instances (instance_id, template_id, status, inputs)
        VALUES (%s, %s, %s, %s)
        """,
        (instance_id, template_id, "running", json.dumps(inputs))
    )

    conn.commit()
    cur.close()
    conn.close()

    return instance_id

def update_workflow_status(instance_id, status, outputs=None):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE workflow_instances
        SET status = %s,
            completed_at = %s,
            outputs = %s
        WHERE instance_id = %s
        """,
        (status, datetime.utcnow(), json.dumps(outputs) if outputs else None, instance_id)
    )

    conn.commit()
    cur.close()
    conn.close()
    

def log_audit_step(
    instance_id,
    step_name,
    started_at,
    completed_at,
    status,
    input_snapshot,
    output_snapshot=None,
    error_message=None
):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO audit_trail (
            instance_id, step_name, started_at, completed_at,
            status, input_snapshot, output_snapshot, error_message
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            instance_id,
            step_name,
            started_at,
            completed_at,
            status,
            json.dumps(input_snapshot),
            json.dumps(output_snapshot) if output_snapshot else None,
            error_message
        )
    )

    conn.commit()
    cur.close()
    conn.close()
    
    
def execute_workflow(template_id: str, inputs: dict):
    template = load_template(template_id)
    instance_id = create_workflow_instance(template_id, inputs)

    # Shared context
    context = inputs.copy()

    for step in template["steps"]:
        step_name = step["name"]
        task_type = step["task_type"]
        output_key = step.get("output_mapping")

        started_at = datetime.utcnow()

        try:
            task_fn = TASK_REGISTRY[task_type]

            # Execute task
            output = task_fn(context, step.get("config"))

            # Save output to context
            if output_key:
                context[output_key] = output

            completed_at = datetime.utcnow()

            # Log success
            log_audit_step(
                instance_id,
                step_name,
                started_at,
                completed_at,
                "success",
                input_snapshot=context,
                output_snapshot=output
            )

        except Exception as e:
            completed_at = datetime.utcnow()

            # Log failure
            log_audit_step(
                instance_id,
                step_name,
                started_at,
                completed_at,
                "failed",
                input_snapshot=context,
                error_message=str(e)
            )

            update_workflow_status(instance_id, "failed")
            return instance_id

    # Workflow completed successfully
    update_workflow_status(instance_id, "completed", outputs=context)
    return instance_id