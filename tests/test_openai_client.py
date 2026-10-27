"""The Responses API translation, checked against the SDK's own types with no network call."""

import json
from types import SimpleNamespace

import pytest
from openai.types.responses import Response

from agent_harness_lab.models import OpenAIClient, from_responses_output, price, to_responses_input


def fake_response(*, with_call: bool = True) -> Response:
    output = [
        {"type": "reasoning", "id": "rs_1", "summary": [], "encrypted_content": "opaque"},
        {"type": "message", "id": "msg_1", "role": "assistant", "status": "completed",
         "content": [{"type": "output_text", "text": "Reading the module.", "annotations": []}]},
    ]
    if with_call:
        output.append({"type": "function_call", "id": "fc_1", "call_id": "call_1", "name": "bash",
                       "arguments": json.dumps({"command": "cat stats.py"})})
    return Response.model_validate({
        "id": "resp_1", "object": "response", "created_at": 0, "model": "gpt-6-luna",
        "output": output, "parallel_tool_calls": False, "tool_choice": "auto", "tools": [],
        "usage": {"input_tokens": 1000, "output_tokens": 200, "total_tokens": 1200,
                  "input_tokens_details": {"cached_tokens": 600, "cache_write_tokens": 100},
                  "output_tokens_details": {"reasoning_tokens": 150}},
    })


def test_output_folds_into_one_chat_message():
    message, calls = from_responses_output(fake_response().output)
    assert message["content"] == "Reading the module."
    assert [call.command for call in calls] == ["cat stats.py"]
    assert message["reasoning"][0]["encrypted_content"] == "opaque"


def test_history_round_trips_into_responses_input():
    message, _ = from_responses_output(fake_response().output)
    history = [
        {"role": "system", "content": "be careful"},
        {"role": "user", "content": "fix it"},
        message,
        {"role": "tool", "tool_call_id": "call_1", "content": "exit code 0\n..."},
    ]
    instructions, items = to_responses_input(history)
    assert instructions == "be careful"
    assert [item.get("type", item.get("role")) for item in items] == [
        "user", "reasoning", "assistant", "function_call", "function_call_output",
    ]
    assert items[3]["call_id"] == items[4]["call_id"] == "call_1"


def test_cached_and_written_tokens_are_billed_at_their_own_rates():
    # 300 uncached at $0.10, 600 cached at $0.01, 100 written at $0.125, 200 output at $0.50.
    expected = (300 * 0.10 + 600 * 0.01 + 100 * 0.125 + 200 * 0.50) / 1_000_000
    assert price("gpt-6-luna", 1000, 200, cached_tokens=600, cache_write_tokens=100) == pytest.approx(expected)


def test_client_sends_a_stateless_reasoning_request(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    client = OpenAIClient("gpt-6-luna", reasoning_effort="low")
    sent = {}

    def create(**kwargs):
        sent.update(kwargs)
        return fake_response(with_call=False)

    client._client = SimpleNamespace(responses=SimpleNamespace(create=create))
    reply = client.complete([{"role": "system", "content": "s"}, {"role": "user", "content": "u"}])
    assert sent["store"] is False
    assert sent["include"] == ["reasoning.encrypted_content"]
    assert sent["reasoning"] == {"effort": "low"}
    assert sent["tools"][0]["name"] == "bash"
    assert reply.tool_calls == []
    assert reply.cost_usd == pytest.approx(price("gpt-6-luna", 1000, 200, 600, 100))


def test_unpriced_model_fails_before_any_call(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    with pytest.raises(KeyError, match="gpt-unknown"):
        OpenAIClient("gpt-unknown")
