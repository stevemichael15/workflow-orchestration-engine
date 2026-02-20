from tasks.mock_data import fetch_citizen, fetch_scheme_rules
from tasks.eligibility import evaluate_rules
from tasks.decision import make_decision
from tasks.report_builder import build_report
from engine.parallel import parallel_execute
from tasks.batch_loader import load_citizen_batch

TASK_REGISTRY = {
    "mock_db_lookup": fetch_citizen,
    "mock_doc_lookup": fetch_scheme_rules,
    "rule_engine": evaluate_rules,
    "decision_logic": make_decision,
    "parallel_execution": parallel_execute,
    "report_builder": build_report,
    "load_citizen_batch": load_citizen_batch
}