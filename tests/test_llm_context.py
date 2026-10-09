from core.llm import _select_history, ask_llm
from core.prompt_builder import build_prompt


def test_history_keeps_most_recent_complete_turns_within_budget():
    history = [
        {"role": "user", "content": "older question"},
        {"role": "assistant", "content": "older answer"},
        {"role": "user", "content": "recent question"},
        {"role": "assistant", "content": "recent answer"},
    ]

    selected = _select_history(history, token_budget=8)

    assert selected == history[-2:]


def test_history_truncates_latest_turn_when_it_exceeds_budget():
    history = [
        {"role": "user", "content": "Question " * 20},
        {"role": "assistant", "content": "Answer " * 100},
    ]

    selected = _select_history(history, token_budget=10)

    assert [message["role"] for message in selected] == ["user", "assistant"]
    assert sum(len(message["content"]) for message in selected) <= 40


def test_rag_prompt_caps_document_context_but_keeps_query():
    chunks = [
        {"source": "guide.pdf", "score": 0.9, "text": "document text " * 500}
    ]

    prompt = build_prompt(
        chunks,
        "What is the approval process?",
        max_context_tokens=50,
    )

    assert "What is the approval process?" in prompt
    assert "Document context truncated" in prompt


def test_ask_llm_uses_selected_context_window_and_chat_history(monkeypatch):
    class FakeClient:
        call = None

        def chat(self, **kwargs):
            self.call = kwargs
            return {"message": {"content": "answer"}}

    fake_client = FakeClient()
    monkeypatch.setattr("core.llm._client", fake_client)
    history = [
        {"role": "user", "content": "Previous question"},
        {"role": "assistant", "content": "Previous answer"},
    ]

    answer = ask_llm(
        "Current question",
        model="test-model",
        history=history,
        num_ctx=4096,
    )

    assert answer == "answer"
    assert fake_client.call["options"]["num_ctx"] == 4096
    assert fake_client.call["messages"] == [
        *history,
        {"role": "user", "content": "Current question"},
    ]
