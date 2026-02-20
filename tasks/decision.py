def make_decision(context, config=None):
    rules_result = context["rule_result"]

    if rules_result["income_near_limit"]:
        return {
            "decision": "NEEDS_REVIEW",
            "reason": "Income close to scheme limit"
        }

    if rules_result["age_pass"] and rules_result["income_pass"]:
        return {
            "decision": "ELIGIBLE",
            "reason": "All eligibility criteria satisfied"
        }

    return {
        "decision": "NOT_ELIGIBLE",
        "reason": "Eligibility criteria not met"
    }