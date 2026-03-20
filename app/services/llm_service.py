from typing import Optional

from ollama import chat

MODEL_NAME = "gemma3"


def _extra_block(extra_context: str) -> str:
    if not extra_context.strip():
        return ""
    return (
        "\n\n---\n"
        "Additional context (authoritative for identity, greetings, product info, and anything it describes).\n"
        "For questions about the repository, still ground answers in Code Context when that section is present.\n"
        "If there is no Code Context, answer from this block when it applies; otherwise say you have no repo evidence.\n\n"
        f"{extra_context.strip()}\n"
    )


def generate_answer(
    question: str,
    code_context: Optional[str],
    extra_context: str = "",
) -> str:
    """
    If code_context is non-empty, answer as a repo assistant using retrieved chunks.
    If code_context is empty, still call the model when extra_context is set (e.g. greetings).
    """
    extra = _extra_block(extra_context)

    system_prompt = (
        "You are DevPilot, an expert backend code assistant.\n\n"
        "Repository questions:\n"
        "- When Code Context is provided below the question, use it as the source of truth for technical answers.\n"
        "- Do not invent files, functions, or behavior that are not supported by that context.\n"
        "- If the answer is not in the code context, say: "
        "'I could not find enough evidence in the retrieved code.'\n\n"
        "Style:\n"
        "- Be clear and concise; use bullets when helpful.\n"
        "- Name files, classes, and functions when citing the repo.\n"
        "- Explain flow and logic when relevant.\n\n"
        f"{extra}"
    )

    if code_context and code_context.strip():
        user_prompt = f"""Question:
{question}

Code Context:
{code_context}

Answer the question. Use Code Context for repo-specific facts."""
    else:
        user_prompt = f"""Question:
{question}

(No code chunks were retrieved from the repository.)

Answer using Additional context when it applies. If it does not apply, say you could not find evidence in the repo."""

    response = chat(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    return response["message"]["content"]


def generate_repo_answer(question: str, context: str) -> str:
    """Backward-compatible wrapper (code only, no extra context)."""
    return generate_answer(question, code_context=context, extra_context="")