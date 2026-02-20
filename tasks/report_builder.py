from collections import defaultdict

from collections import Counter

def build_report(context, config=None):
    results = context["parallel_results"]["results"]

    decision_counts = Counter(
        item["decision"] for item in results
    )

    return {
        "total": len(results),
        "eligible": decision_counts.get("ELIGIBLE", 0),
        "not_eligible": decision_counts.get("NOT_ELIGIBLE", 0),
        "needs_review": decision_counts.get("NEEDS_REVIEW", 0)
    }