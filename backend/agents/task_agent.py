import json
from services.mistral_client import call_mistral
from agents.utils import clean_json
from models.schemas import TaskResponse

MODEL = "mistral-large-latest"

SYSTEM_PROMPT = """
You are a Senior Project Manager writing a Work Breakdown Structure.

Generate tasks for ONE phase in simple, clear language that a client,
developer, and project manager can all understand without explanation.

RULES:
- Task titles must be feature names not technical actions
- Never write task titles like "Implement RESTful API" or "Develop Database Schema"
- Write task titles like "Search Profiles", "Member Registration", "Payment Management"
- Detailed information must be simple sub-features separated by " | "
- No technical jargon anywhere
- Do not use bullet symbols, newlines, or special characters in detailed_information
- Keep detailed_information as a single clean line
- Match task count strictly to project complexity:
  Simple app = 5-8 tasks per phase, Medium = 8-12, Complex enterprise = 12-15
- One task must cover an entire feature, not individual components
- Do not generate documentation or user feedback tasks
- Module Name must be the feature area, never the phase name
- Group all tasks strictly by module name
- Owner must be a simple role like "Frontend Developer", "Backend Developer", "QA Engineer"
- Priority: High, Medium, or Low
- Status: always "Pending"
- percent_complete: always "0%"
- delay_days: always 0
- actual_completion_date: always empty
- effort_hours: always 0

DELIVERY CONFIGURATION RULES:
- If ui_ux = "Y", include wireframe and design tasks
- If frontend = "Y", include frontend tasks
- If backend = "Y", include backend tasks
- If mobile_native = "Y", include Android and iOS tasks
- If mobile_hybrid = "Y", include Flutter or React Native tasks
- If api = "Y", include API development tasks
- If api_integration = "Y", include third party integration tasks
- If testing_deployment = "Y", include testing, UAT and deployment tasks
- If source_code_delivery = "Y", include source code handover task in final phase
- If free_support_30 = "Y", include 30 days post go-live support task in final phase
- If free_support_45 = "Y", include 45 days post go-live support task in final phase
- If any config = "N", do not include those tasks

RETURN VALID JSON ONLY

FORMAT:
{
  "tasks": [
    {
      "task_id": "1",
      "module_name": "Member Registration",
      "task_title": "Sign Up Module",
      "detailed_information": "Email and Password Registration | Video Verification | Social Login (Google, Facebook, Apple)",
      "priority": "High",
      "dependency": "-",
      "owner": "Frontend Developer",
      "status": "Pending",
      "start_date": "01-Jun-26",
      "working_duration_days": 3,
      "actual_completion_date": "",
      "delay_days": 0,
      "percent_complete": "0%",
      "effort_hours": 0,
      "sprint_milestone": "Sprint 1",
      "remarks_comments": ""
    }
  ]
}
"""


async def run_task_agent(
    detailed_scope: str,
    modules: dict,
    project_config: dict,
    phase_name: str,
    assigned_modules: list,
    previous_context: str,
    team_size: int,
    project_start_date: str,
) -> tuple[dict, dict]:

    user_prompt = f"""
PROJECT SCOPE:
{detailed_scope}

GLOBAL MODULES:
{json.dumps(modules, indent=2)}

DELIVERY CONFIGURATION:
{json.dumps(project_config, indent=2)}

PREVIOUSLY GENERATED TASKS:
{previous_context}

CURRENT PHASE:
{phase_name}

ASSIGNED MODULES:
{json.dumps(assigned_modules, indent=2)}

TEAM SIZE:
{team_size}

PROJECT START DATE:
{project_start_date}

IMPORTANT:
- Do NOT duplicate previous tasks
- Do NOT repeat completed architecture work
- Generate only NEW work relevant to this phase
"""

    for attempt in range(3):
        content, tokens = await call_mistral(MODEL, SYSTEM_PROMPT, user_prompt)
        try:
            task_json = TaskResponse.model_validate_json(clean_json(content))
            return task_json.model_dump(), tokens
        except Exception:
            if attempt == 2:
                raise RuntimeError(f"Task agent failed to return valid JSON for phase: {phase_name}")
            continue
    return {"tasks": []}, {}
