import os
from dotenv import load_dotenv
load_dotenv()  # Must run before any module that reads env vars at import time

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from graph import devfix_graph
from state import AgentState
import time

app = FastAPI(title="DevFix Auto-Agent API", version="1.0")

class TaskRequest(BaseModel):
    task: str

@app.post("/run-task")
async def run_task(request: TaskRequest):
    start_time = time.time()
    initial_state: AgentState = {
        "task": request.task,
        "messages": [],
        "code": "",
        "error": "",
        "test_results": "",
        "attempts": 0,
        "approved": True,           # Auto-approve in API mode
        "total_cost": 0.0,
        "latency_ms": 0.0,
        "audit_log": [],
        "run_id": None
    }

    try:
        final_state = None
        for event in devfix_graph.stream(initial_state, stream_mode="values"):
            final_state = event

        total_time = (time.time() - start_time) * 1000
        final_state["latency_ms"] = total_time

        return {
            "success": "passed" in final_state.get("test_results", ""),
            "code": final_state.get("code", ""),
            "attempts": final_state.get("attempts", 0),
            "latency_ms": final_state["latency_ms"],
            "status": "success" if "passed" in final_state.get("test_results", "") else "failed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy"}