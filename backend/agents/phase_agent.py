import json
from services.mistral_client import call_mistral
from agents.utils import clean_json
from models.schemas import PhaseResponse

MODEL = "mistral-small-latest"

SYSTEM_PROMPT = """
You are a Senior Project Manager.

Generate delivery phases for the project based on the scope, modules, and delivery configuration provided.

RULES:
- Phases must reflect how a real team actually works and delivers
- Use simple human phase names like:
  "Design & Planning", "UI/UX Design", "Frontend Development",
  "Backend Development", "Mobile Development", "Admin Panel", "UAT & Deployment"
- Do not use enterprise or technical phase names
- Match phase count strictly to project size:
  Simple app = max 3 phases, Medium = 4 phases, Complex enterprise = 5-6 phases
- Combine Design and Frontend into one phase for simple projects
- Each module must appear in at least one phase
- Security and Testing are not standalone phases
- UAT and Deployment must always be combined into one final phase

DELIVERY CONFIGURATION RULES:
- If business_analysis = "Y", include a Design & Planning phase
- If ui_ux = "Y", include UI/UX Design phase
- If frontend = "Y", include Frontend Development phase
- If backend = "Y", include Backend Development phase
- If mobile_native = "Y", include Native Mobile Development phase
- If mobile_hybrid = "Y", include Mobile Development phase
- If testing_deployment = "Y", include UAT & Deployment as final phase
- If source_code_delivery = "Y", add source code handover to final phase
- If free_support_30 = "Y" or free_support_45 = "Y", add post go-live support to final phase
- If any config = "N", do not include that phase

RETURN VALID JSON ONLY

FORMAT:
{
  "phases": [
    {
      "phase_name": "Design & Planning",
      "modules": ["Member Registration", "Search & Discovery"]
    }
  ]
}
"""


async def run_phase_agent(detailed_scope: str, modules: dict, project_config: dict) -> tuple[dict, dict]:
    user_prompt = f"""
PROJECT SCOPE:
{detailed_scope}

GLOBAL MODULES:
{json.dumps(modules, indent=2)}

DELIVERY CONFIGURATION:
{json.dumps(project_config, indent=2)}
"""
    for attempt in range(3):
        content, tokens = await call_mistral(MODEL, SYSTEM_PROMPT, user_prompt)
        try:
            phase_json = PhaseResponse.model_validate_json(clean_json(content))
            return phase_json.model_dump(), tokens
        except Exception:
            if attempt == 2:
                raise RuntimeError("Phase agent failed to return valid JSON")
            continue
    return {"phases": []}, {}
