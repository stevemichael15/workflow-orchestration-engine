from fastapi import FastAPI
from api.routes import router

app = FastAPI(
    title="Workflow Orchestration Engine",
    description="Template-driven workflow engine with audit logs and appeal processing",
    version="1.0.0"
)

app.include_router(router)