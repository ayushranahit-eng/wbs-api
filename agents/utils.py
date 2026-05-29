def clean_json(output: str) -> str:
    cleaned = output.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned.replace("```json", "", 1)
    if cleaned.startswith("```"):
        cleaned = cleaned.replace("```", "", 1)
    if cleaned.endswith("```"):
        cleaned = cleaned.rsplit("```", 1)[0]
    return cleaned.strip()
