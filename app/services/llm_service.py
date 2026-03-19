from ollama import chat

MODEL_NAME = "gemma3"


def generate_repo_answer(question: str, context: str) -> str:
    system_prompt = (
        "You are DevPilot, a backend code assistant. "
        "Answer only from the provided code context. "
        "If the answer is not supported by the context, say: "
        "'I could not find enough evidence in the retrieved code.' "
        "Keep the answer clear and concise."
    )

    user_prompt = f"""
Question:
{question}

Code Context:
{context}

Answer the question using only the code context above.
"""

    response = chat(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    return response["message"]["content"]