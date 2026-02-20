from concurrent.futures import ThreadPoolExecutor, as_completed
from tasks.mock_data import generate_citizen, fetch_scheme_rules
from tasks.eligibility import evaluate_rules
from tasks.decision import make_decision

def run_single_evaluation(citizen_id: str, scheme_name: str):
    try:
        # Build local context (isolated per thread)
        context = {
            "citizen_id": citizen_id,
            "scheme_name": scheme_name
        }

        citizen = generate_citizen(citizen_id)
        scheme_rules = fetch_scheme_rules(context)

        context["citizen"] = citizen
        context["scheme_rules"] = scheme_rules

        rule_result = evaluate_rules(context)
        context["rule_result"] = rule_result

        decision = make_decision(context)

        return {
            "citizen_id": citizen_id,
            "decision": decision["decision"]
        }

    except Exception as e:
        raise RuntimeError(str(e))
      
def parallel_execute(context, config=None):
    citizens = context["citizens"]
    scheme_name = context["scheme_name"]

    max_workers = config.get("max_workers", 20) if config else 20

    results = []
    failures = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {
            executor.submit(run_single_evaluation, citizen_id, scheme_name): citizen_id
            for citizen_id in citizens
        }

        for future in as_completed(future_map):
            citizen_id = future_map[future]

            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                failures.append({
                    "citizen_id": citizen_id,
                    "error": str(e)
                })

    return {
        "results": results,
        "failures": failures,
        "total": len(citizens),
        "success_count": len(results),
        "failure_count": len(failures)
    }