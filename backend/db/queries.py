from datetime import datetime, timezone
from db.mongo_client import get_db


async def create_job(job_id: str, payload: dict):
    await get_db().wbs_jobs.insert_one({
        "_id": job_id,
        "project_title": payload.get("project_title"),
        "company_name": payload.get("company_name"),
        "project_manager": payload.get("project_manager"),
        "team_size": payload.get("team_size"),
        "project_start_date": payload.get("project_start_date"),
        "rough_scope": payload.get("rough_scope"),
        "project_config": payload.get("project_config"),
        "recipient_email": payload.get("recipient_email"),
        "status": "pending",
        "error": None,
        "created_at": datetime.now(timezone.utc),
        "completed_at": None,
    })


async def update_job_status(job_id: str, status: str, error: str = None):
    update = {"status": status}
    if status in ("done", "failed"):
        update["completed_at"] = datetime.now(timezone.utc)
    if error:
        update["error"] = error
    await get_db().wbs_jobs.update_one({"_id": job_id}, {"$set": update})


async def get_job(job_id: str):
    return await get_db().wbs_jobs.find_one({"_id": job_id})


async def list_jobs():
    cursor = get_db().wbs_jobs.find().sort("created_at", -1).limit(50)
    jobs = await cursor.to_list(length=50)
    for job in jobs:
        job["_id"] = str(job["_id"])
        if job.get("created_at"):
            job["created_at"] = job["created_at"].isoformat()
        if job.get("completed_at"):
            job["completed_at"] = job["completed_at"].isoformat()
    return jobs
