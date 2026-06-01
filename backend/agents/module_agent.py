import json
from services.mistral_client import call_mistral
from agents.utils import clean_json
from models.schemas import ModuleResponse

MODEL = "mistral-large-latest"

SYSTEM_PROMPT = """
You are a Senior Project Manager.

Extract the main feature areas from the project scope.

RULES:
- Modules must represent real features of the system a user will actually use
- Each module must be distinct with no overlap
- Name modules the way a client would name them, not a developer
- No technical names, no architecture terms
- Module count must match the actual scope, not be padded

GOOD EXAMPLES:
- Member Registration
- Search & Discovery
- Payment Management
- Admin Panel
- Job Portal

BAD EXAMPLES:
- Authentication Service
- REST API Layer
- Database Schema
- Backend Module
- Integration Engine

RETURN VALID JSON ONLY

FORMAT:
{
  "modules": [
    {
      "module_name": "Member Registration",
      "description": "How users sign up, log in and manage their accounts"
    }
  ]
}
"""


async def run_module_agent(detailed_scope: str) -> tuple[dict, dict]:
    for attempt in range(3):
        content, tokens = await call_mistral(MODEL, SYSTEM_PROMPT, detailed_scope)
        try:
            module_json = ModuleResponse.model_validate_json(clean_json(content))
            return module_json.model_dump(), tokens
        except Exception:
            if attempt == 2:
                raise RuntimeError("Module agent failed to return valid JSON")
            continue
    return {"modules": []}, {}
