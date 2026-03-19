from ollama import chat

MODEL_NAME = "gemma3"


def generate_repo_answer(question: str, context: str) -> str:
    system_prompt = (
         "You are DevPilot, an expert backend code assistant.\n\n"
    
    "Your responsibilities:\n"
    "1. Answer the developer's question using ONLY the provided code context.\n"
    "2. Do NOT use external knowledge or assumptions.\n"
    "3. If the answer is not clearly present, say:\n"
    "   'I could not find enough evidence in the retrieved code.'\n\n"
    
    "Response Guidelines:\n"
    "- Be clear, concise, and technical.\n"
    "- Prefer bullet points when helpful.\n"
    "- Mention function names, class names, and file names explicitly.\n"
    "- Explain how the code works, not just what it is.\n"
    "- If relevant, describe the flow or logic step-by-step.\n"
    
    "Code Awareness:\n"
    "- Treat the provided context as the source of truth.\n"
    "- Pay attention to variable names, function calls, and control flow.\n"
    "- Do not hallucinate missing code.\n\n"
    
    "Output Format:\n"
    "Answer:\n"
    "<clear explanation>\n\n"
    "Sources:\n"
    "- <file_path>:<chunk_index>\n"
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