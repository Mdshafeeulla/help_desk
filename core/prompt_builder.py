# core/prompt_builder.py


def build_prompt(chunks: list[dict], question: str, department: str) -> str:
    """
    Build a structured prompt for the LLM.
    Includes department context and source attribution.
    """
    context_parts = []
    for i, c in enumerate(chunks, 1):
        context_parts.append(
            f"[Document {i}: {c['source']} | Relevance: {c['score']:.2f}]\n"
            f"{c['text']}"
        )
    context = "\n\n---\n\n".join(context_parts)

    return f"""You are a knowledgeable AI assistant for the **{department.upper()}** department.

## Rules
1. If the user is just saying hello, greeting you, or making casual conversation, respond politely and naturally without referring to the documents.
2. For domain-specific questions, answer using ONLY the context documents provided below.
3. If the answer to a question is NOT in the context, say: "I don't have enough information in the {department} documents to answer this."
4. Do NOT make up information or use knowledge outside the provided context for factual questions.
5. Cite which document(s) you used in your answer (e.g., "According to Document 2...").
6. Use markdown formatting for clarity.

## Context Documents ({department.upper()} department only)
{context}

## Question
{question}

## Answer"""
