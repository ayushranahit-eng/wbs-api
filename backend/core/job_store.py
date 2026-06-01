import asyncio
from typing import Dict, Any

_jobs: Dict[str, Dict[str, Any]] = {}
_queues: Dict[str, asyncio.Queue] = {}


def create_job(job_id: str):
    _jobs[job_id] = {"status": "pending", "events": [], "result": None, "error": None}
    _queues[job_id] = asyncio.Queue()


def get_job(job_id: str):
    return _jobs.get(job_id)


async def push_event(job_id: str, payload: dict):
    if job_id in _jobs:
        _jobs[job_id]["events"].append(payload)
    if job_id in _queues:
        await _queues[job_id].put({"event": "progress", "data": payload})


async def push_done(job_id: str, result: dict):
    _jobs[job_id]["status"] = "done"
    _jobs[job_id]["result"] = result
    await _queues[job_id].put({"event": "done", "data": result})


async def push_error(job_id: str, error: str):
    _jobs[job_id]["status"] = "failed"
    _jobs[job_id]["error"] = error
    await _queues[job_id].put({"event": "error", "data": {"message": error}})


def get_queue(job_id: str) -> asyncio.Queue:
    return _queues.get(job_id)


def set_running(job_id: str):
    if job_id in _jobs:
        _jobs[job_id]["status"] = "running"
