def evaluate_rules(context, config=None):
    citizen = context["citizen"]
    rules = context["scheme_rules"]

    age_pass = rules["min_age"] <= citizen["age"] <= rules["max_age"]
    income_pass = citizen["income"] <= rules["max_income"]

    income_near_limit = (
        citizen["income"] >= 0.9 * rules["max_income"]
        and citizen["income"] <= rules["max_income"]
    )

    return {
        "age_pass": age_pass,
        "income_pass": income_pass,
        "income_near_limit": income_near_limit
    }