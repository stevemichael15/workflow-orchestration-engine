def load_citizen_batch(context, config=None):
    # Generate 500 deterministic citizen IDs
    return [f"CIT_BATCH_{i}" for i in range(1, 501)]