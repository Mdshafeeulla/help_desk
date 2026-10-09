# core/prompt_builder.py


def build_prompt(
    chunks: list[dict],
    question: str,
    department: str = "it",
    max_context_tokens: int | None = None,
) -> str:
    """
    Build a structured prompt for the MSU Corp support LLM.
    Grounds the answer in retrieved support knowledge base documents.
    """
    context_parts = []
    remaining_chars = max_context_tokens * 4 if max_context_tokens is not None else None
    for i, c in enumerate(chunks, 1):
        header = (
            f"[Support Doc {i}: {c['source']} | Relevance: {c['score']:.2f}]\n"
        )
        text = c["text"]
        if remaining_chars is not None:
            available_text_chars = remaining_chars - len(header)
            if available_text_chars <= 0:
                break
            if len(text) > available_text_chars:
                text = text[:available_text_chars].rsplit(" ", 1)[0]
                context_parts.append(
                    f"{header}{text}\n[Document context truncated to fit the selected context window.]"
                )
                break
            remaining_chars -= len(header) + len(text)
        context_parts.append(f"{header}{text}")
    context = "\n\n---\n\n".join(context_parts)

    return f"""You are the **MSU Corp Support Assistant** — an AI-powered L1 customer support agent for MSU Corp.

## Your Role
You replace the human L1 support team. Customers contact you when they face issues, errors, or have questions about the MSU Corp platform. Your job is to:
- Understand the customer's problem clearly
- Find the relevant solution from the official support knowledge base below
- Provide a clear, step-by-step resolution in a friendly, professional tone
- If the issue is not covered, guide the customer on how to escalate

## Rules
1. **Greetings / casual chat**: Respond warmly and briefly, then ask what issue they're facing.
2. **Platform issues**: Answer using ONLY the support knowledge base documents provided below. Be specific and actionable.
3. **Unknown issues**: If the answer is NOT in the knowledge base, say: *"I don't have a documented solution for this issue in our knowledge base. Please contact our support team at support@msucorp.com or raise a ticket for further assistance."*
4. **Never fabricate**: Do NOT make up steps, solutions, or policies not present in the documents.
5. **Cite your sources**: Reference which support document you used (e.g., "According to Support Doc 2...").
6. **Tone**: Be professional, empathetic, and concise. Customers want fast resolutions.
7. **Formatting**: Use markdown — bullet points, numbered steps, bold for key terms.

## MSU Corp Support Knowledge Base
{context}

## Customer Query
{question}

## Support Response"""
