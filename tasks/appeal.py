from db.connection import get_connection

def load_original_instance(context, config=None):
    original_id = context["original_instance_id"]

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT status, outputs
        FROM workflow_instances
        WHERE instance_id = %s
        """,
        (original_id,)
    )

    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        raise ValueError("Original workflow instance not found")

    status, outputs = row

    if status != "completed":
        raise ValueError("Original workflow is not completed")

    return {
        "instance_id": original_id,
        "outputs": outputs
    }
    
def validate_evidence(context, config=None):
    new_data = context["new_data"]

    allowed_fields = {"age", "income", "category"}

    for key in new_data.keys():
        if key not in allowed_fields:
            raise ValueError(f"Invalid evidence field: {key}")

    return new_data
  
def compare_decisions(context, config=None):
    old_decision = context["original_instance"]["outputs"]["decision"]
    new_decision = context["decision"]["decision"]

    changed_fields = list(context["validated_data"].keys())

    return {
        "decision_changed": old_decision != new_decision,
        "old_decision": old_decision,
        "new_decision": new_decision,
        "changed_fields": changed_fields
    }
    
def record_appeal(context, config=None):
    conn = get_connection()
    cur = conn.cursor()

    outcome = "accepted" if context["decision_comparison"]["decision_changed"] else "rejected"

    cur.execute(
        """
        INSERT INTO appeals (appeal_of, new_instance_id, outcome)
        VALUES (%s, %s, %s)
        """,
        (
            context["original_instance"]["instance_id"],
            context["new_instance_id"],
            outcome
        )
    )

    conn.commit()
    cur.close()
    conn.close()

    return {
        "outcome": outcome
    }
