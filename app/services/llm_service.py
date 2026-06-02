import asyncio


async def generate_llm_response(text: str) -> str:
    await asyncio.sleep(2)

    if "force_llm_error" in text:
        raise RuntimeError("Simulated LLM failure")

    return f"Simulated LLM response for: {text}"
