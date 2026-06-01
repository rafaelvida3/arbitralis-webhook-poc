import asyncio


async def generate_llm_response(text: str) -> str:
    await asyncio.sleep(2)

    return f"Simulated LLM response for: {text}"