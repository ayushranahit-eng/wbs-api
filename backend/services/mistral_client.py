import asyncio
from mistralai.client import Mistral
from core.config import settings

client = Mistral(api_key=settings.MISTRAL_API_KEY)


async def call_mistral(
    model: str,
    system_prompt: str,
    user_prompt: str,
    retries: int = 3,
    retry_delay: int = 5,
) -> tuple[str, dict]:
    """
    Returns (content, token_usage)
    token_usage = { input_tokens, output_tokens }
    """
    last_error = None

    for attempt in range(retries):
        try:
            response = await asyncio.to_thread(
                client.chat.complete,
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
            )

            content = response.choices[0].message.content
            usage = response.usage

            token_usage = {
                "input_tokens": usage.prompt_tokens if usage else 0,
                "output_tokens": usage.completion_tokens if usage else 0,
            }

            return content, token_usage

        except Exception as e:
            last_error = e
            if attempt < retries - 1:
                wait = retry_delay * (attempt + 1)
                await asyncio.sleep(wait)

    raise RuntimeError(f"Mistral call failed after {retries} attempts: {last_error}")
