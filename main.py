import asyncio
import json
import uuid
import os
from datetime import datetime

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

from models.schemas import (
    WBSRequest, JobResponse,
    ScopeRequest, ModuleRequest, PhaseRequest, TaskRequest,
)
from core.job_store import (
    create_job, get_job, get_queue,
    push_event, push_done, push_error, set_running,
)
from agents.scope_agent import run_scope_agent
from agents.module_agent import run_module_agent
from agents.phase_agent import run_phase_agent
from agents.task_agent import run_task_agent
from services.excel_builder import build_excel, build_rows
from services.mail_service import send_wbs_email
from db import queries
from core.config import settings

app = FastAPI(title="WBS AI System", version="1.0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# BACKGROUND PIPELINE
# ─────────────────────────────────────────────

async def run_wbs_pipeline(job_id: str, req: WBSRequest):
    set_running(job_id)
    await queries.update_job_status(job_id, "running")

    project_config = {k: v.upper() for k, v in req.project_config.model_dump().items()}

    try:
        # STEP 1 – SCOPE
        await push_event(job_id, {"step": 1, "agent": "Scope Agent", "status": "running"})
        detailed_scope, _ = await run_scope_agent(req.rough_scope)
        await push_event(job_id, {"step": 1, "agent": "Scope Agent", "status": "done", "result": detailed_scope})

        # STEP 2 – MODULES
        await push_event(job_id, {"step": 2, "agent": "Module Agent", "status": "running"})
        module_json, _ = await run_module_agent(detailed_scope)
        module_names = [m["module_name"] for m in module_json["modules"]]
        await push_event(job_id, {"step": 2, "agent": "Module Agent", "status": "done", "result": module_names})

        # STEP 3 – PHASES
        await push_event(job_id, {"step": 3, "agent": "Phase Agent", "status": "running"})
        phase_json, _ = await run_phase_agent(detailed_scope, module_json, project_config)
        phases = phase_json.get("phases", [])
        phase_names = [p["phase_name"] for p in phases]
        await push_event(job_id, {"step": 3, "agent": "Phase Agent", "status": "done", "result": phase_names})

        # STEP 4 – TASKS
        all_rows = []
        global_task_id = 1
        global_sub_task_id = 1
        previous_context = ""
        total_phases = len(phases)

        for index, phase in enumerate(phases, start=1):
            phase_name = phase.get("phase_name", "")
            assigned_modules = phase.get("modules", [])

            await push_event(job_id, {"step": 4, "agent": "Task Agent", "status": "running", "phase": phase_name, "phase_index": index, "total_phases": total_phases})

            task_json, _ = await run_task_agent(
                detailed_scope=detailed_scope,
                modules=module_json,
                project_config=project_config,
                phase_name=phase_name,
                assigned_modules=assigned_modules,
                previous_context=previous_context,
                team_size=req.team_size,
                project_start_date=req.project_start_date,
            )

            tasks = task_json.get("tasks", [])
            rows, global_task_id, global_sub_task_id = build_rows(
                tasks, phase_name, global_task_id, global_sub_task_id
            )
            all_rows.extend(rows)

            previous_context += f"\nPHASE: {phase_name}\n"
            for t in tasks:
                previous_context += f"  Module: {t.get('module_name')} | Task: {t.get('task_title')}\n"

            await push_event(job_id, {"step": 4, "agent": "Task Agent", "status": "done", "phase": phase_name, "phase_index": index, "total_phases": total_phases, "task_count": len(tasks)})

        # BUILD EXCEL
        await push_event(job_id, {"step": 5, "agent": "Excel Builder", "status": "running"})
        full_path, sales_path = build_excel(
            all_rows,
            req.project_title,
            req.company_name,
            req.project_manager,
            job_id,
        )
        await push_event(job_id, {"step": 5, "agent": "Excel Builder", "status": "done"})

        # EMAIL
        if req.recipient_email:
            await push_event(job_id, {"step": 6, "agent": "Email Service", "status": "running", "recipient": str(req.recipient_email)})
            await asyncio.to_thread(
                send_wbs_email,
                req.recipient_email,
                req.project_title,
                full_path,
                sales_path,
            )
            await push_event(job_id, {"step": 6, "agent": "Email Service", "status": "done", "recipient": str(req.recipient_email)})

        await queries.update_job_status(job_id, "done")
        await push_done(job_id, {"full_wbs_local": full_path, "sales_wbs_local": sales_path})

    except Exception as e:
        error_msg = str(e)
        await queries.update_job_status(job_id, "failed", error=error_msg)
        await push_error(job_id, error_msg)


# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────

@app.post("/generate-wbs", response_model=JobResponse, tags=["WBS Pipeline"])
async def generate_wbs(req: WBSRequest, background_tasks: BackgroundTasks):
    """Submit a WBS generation job. Returns job_id immediately."""
    job_id = str(uuid.uuid4())
    create_job(job_id)
    await queries.create_job(job_id, {
        "project_title": req.project_title,
        "company_name": req.company_name,
        "project_manager": req.project_manager,
        "team_size": req.team_size,
        "project_start_date": req.project_start_date,
        "rough_scope": req.rough_scope,
        "project_config": req.project_config.model_dump(),
        "recipient_email": str(req.recipient_email) if req.recipient_email else None,
    })
    background_tasks.add_task(run_wbs_pipeline, job_id, req)
    return JobResponse(job_id=job_id, message="WBS generation started. Connect to /status/{job_id} for live updates.")


@app.get("/status/{job_id}", tags=["WBS Pipeline"])
async def stream_status(job_id: str):
    """SSE stream for live progress updates of a job."""
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    queue = get_queue(job_id)

    async def event_generator():
        for payload in job.get("events", []):
            yield f"event: progress\ndata: {json.dumps(payload)}\n\n"

        if job["status"] in ("done", "failed"):
            if job["status"] == "done":
                yield f"event: done\ndata: {json.dumps(job['result'])}\n\n"
            else:
                yield f"event: error\ndata: {json.dumps({'message': job['error']})}\n\n"
            return

        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=60)
                yield f"event: {event['event']}\ndata: {json.dumps(event['data'])}\n\n"
                if event["event"] in ("done", "error"):
                    break
            except asyncio.TimeoutError:
                yield f"event: ping\ndata: {{}}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/job/{job_id}", tags=["WBS Pipeline"])
async def get_job_details(job_id: str):
    """Get job input + status from MongoDB."""
    job = await queries.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job["_id"] = str(job["_id"])
    return job


@app.get("/download/{job_id}/{file_type}", tags=["WBS Pipeline"])
async def download_file(job_id: str, file_type: str):
    """Direct download: file_type = full_wbs or sales_wbs"""
    job = get_job(job_id)
    if not job or not job.get("result"):
        raise HTTPException(status_code=404, detail="Job not ready or not found")

    key = "full_wbs_local" if file_type == "full_wbs" else "sales_wbs_local"
    path = job["result"].get(key)

    if not path or not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found on server")

    return FileResponse(
        path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=os.path.basename(path),
    )


# ─────────────────────────────────────────────
# INDIVIDUAL AGENT ENDPOINTS
# ─────────────────────────────────────────────

@app.post("/agents/scope", tags=["Individual Agents"])
async def agent_scope(req: ScopeRequest):
    content, tokens = await run_scope_agent(req.rough_scope)
    return {"scope": content, "tokens": tokens}


@app.post("/agents/modules", tags=["Individual Agents"])
async def agent_modules(req: ModuleRequest):
    modules, tokens = await run_module_agent(req.detailed_scope)
    return {"modules": modules, "tokens": tokens}


@app.post("/agents/phases", tags=["Individual Agents"])
async def agent_phases(req: PhaseRequest):
    phases, tokens = await run_phase_agent(
        req.detailed_scope,
        req.modules,
        req.project_config.model_dump(),
    )
    return {"phases": phases, "tokens": tokens}


@app.post("/agents/tasks", tags=["Individual Agents"])
async def agent_tasks(req: TaskRequest):
    phases = req.phases.get("phases", [])
    all_tasks = []
    previous_context = ""
    for phase in phases:
        task_json, tokens = await run_task_agent(
            detailed_scope=req.detailed_scope,
            modules=req.modules,
            project_config=req.project_config.model_dump(),
            phase_name=phase["phase_name"],
            assigned_modules=phase["modules"],
            previous_context=previous_context,
            team_size=req.team_size,
            project_start_date=req.project_start_date,
        )
        all_tasks.append({"phase": phase["phase_name"], "tasks": task_json, "tokens": tokens})
        for t in task_json.get("tasks", []):
            previous_context += f"  Module: {t.get('module_name')} | Task: {t.get('task_title')}\n"
    return {"phases_tasks": all_tasks}


@app.get("/jobs", tags=["WBS Pipeline"])
async def list_jobs():
    """Get all recent jobs from MongoDB."""
    jobs = await queries.list_jobs()
    return jobs


@app.get("/config", tags=["System"])
async def get_config():
    return {"api_base_url": settings.API_BASE_URL}


@app.get("/health", tags=["System"])
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}
