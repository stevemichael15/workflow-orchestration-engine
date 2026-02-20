# tasks/mock_data.py

import random

SCHEMES = {
    "scheme_alpha": {"min_age": 18, "max_age": 60, "max_income": 250000},
    "scheme_beta": {"min_age": 21, "max_age": 55, "max_income": 180000},
    "scheme_gamma": {"min_age": 60, "max_age": 99, "max_income": 120000},
}


def generate_citizen(citizen_id: str) -> dict:
    random.seed(hash(citizen_id))

    return {
        "name": f"Citizen_{citizen_id}",
        "age": random.randint(18, 80),
        "income": random.randint(50000, 300000),
        "category": random.choice(["general", "sc", "st", "obc"])
    }


def fetch_citizen(context, config=None):
    citizen = generate_citizen(context["citizen_id"])

    # override with appeal data if present
    for field in ["age", "income", "category"]:
        if field in context:
            citizen[field] = context[field]

    return citizen


def fetch_scheme_rules(context, config=None):
    scheme_name = context["scheme_name"]

    if scheme_name not in SCHEMES:
        raise ValueError(f"Unknown scheme: {scheme_name}")

    return SCHEMES[scheme_name]
