from pydantic import BaseModel, EmailStr
from typing import Optional, List


class ProjectConfig(BaseModel):
    business_analysis: str
    ui_ux: str
    frontend: str
    backend: str
    mobile_native: str
    mobile_hybrid: str
    api: str
    api_integration: str
    testing_deployment: str
    source_code_delivery: str
    free_support_30: str
    free_support_45: str


class WBSRequest(BaseModel):
    project_title: str
    company_name: str
    project_manager: str
    team_size: int
    project_start_date: str
    rough_scope: str
    project_config: ProjectConfig
    recipient_email: Optional[EmailStr] = None


class JobResponse(BaseModel):
    job_id: str
    message: str


class ScopeRequest(BaseModel):
    rough_scope: str


class ModuleRequest(BaseModel):
    detailed_scope: str


class PhaseRequest(BaseModel):
    detailed_scope: str
    modules: dict
    project_config: ProjectConfig


class TaskRequest(BaseModel):
    detailed_scope: str
    modules: dict
    phases: dict
    project_config: ProjectConfig
    team_size: int
    project_start_date: str


# ── Mistral response models ──

class Task(BaseModel):
    task_id: str
    module_name: str
    task_title: str
    detailed_information: str
    priority: str
    dependency: str = "-"
    owner: str
    status: str = "Pending"
    start_date: str = ""
    working_duration_days: int = 0
    actual_completion_date: str = ""
    delay_days: int = 0
    percent_complete: str = "0%"
    effort_hours: int = 0
    sprint_milestone: str = ""
    remarks_comments: str = ""


class TaskResponse(BaseModel):
    tasks: List[Task]


class Module(BaseModel):
    module_name: str
    description: str


class ModuleResponse(BaseModel):
    modules: List[Module]


class Phase(BaseModel):
    phase_name: str
    modules: List[str]


class PhaseResponse(BaseModel):
    phases: List[Phase]
