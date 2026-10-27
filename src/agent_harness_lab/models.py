"""The OpenAI client the agent loop talks to.

The loop keeps its history in the chat-completions message format, which is
compact and easy to read in transcripts. The OpenAI client translates that
history into Responses API input at the last moment, because the GPT-6 models
only combine reasoning with tool calls through the Responses API.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Settings come from the repository's .env file when one exists. Variables already
# set in the shell take precedence, so a one-off override needs no file edit.
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

DEFAULT_MODEL = os.environ.get("OPENAI_MODEL", "gpt-6-luna")
# Reasoning tokens are billed as output, so effort is the main lever on cost.
REASONING_EFFORT = os.environ.get("OPENAI_REASONING_EFFORT", "low")


@dataclass(frozen=True)
class Price:
    """US dollars per million tokens for one model."""

    input: float
    cached_input: float
    cache_write: float
    output: float


# Standard-tier prices from OpenAI's pricing page as of October 2026. Prices
# change, so these deserve a check before a real run.
PRICES_PER_MILLION = {
    "gpt-6-luna": Price(input=0.10, cached_input=0.01, cache_write=0.125, output=0.50),
    "gpt-6-sol": Price(input=2.00, cached_input=0.20, cache_write=2.50, output=10.00),
    "gpt-5.6-luna": Price(input=0.20, cached_input=0.02, cache_write=0.25, output=1.20),
}

BASH_TOOL = {
    "type": "function",
    "name": "bash",
    "description": "Run a shell command in the repository and return its combined output.",
    "parameters": {
        "type": "object",
        "properties": {"command": {"type": "string", "description": "The command to run."}},
        "required": ["command"],
        "additionalProperties": False,
    },
    "strict": True,
}


@dataclass(frozen=True)
class ToolCall:
    id: str
    command: str


@dataclass(frozen=True)
class ModelReply:
    """One model turn.

    Attributes:
        message: The assistant message, in chat-completions format, ready to be
            appended to the conversation. A real model's message also carries
            its encrypted reasoning under "reasoning", for replay on later turns.
        tool_calls: Commands the model asked to run; empty when it declares the
            task done.
        output_tokens: Visible output plus reasoning tokens, as billed.
    """

    message: dict
    tool_calls: list[ToolCall]
    input_tokens: int
    output_tokens: int
    cost_usd: float


def tool_call_message(call: ToolCall) -> dict:
    """Formats a bash call the way a chat-completions history records it."""
    return {
        "id": call.id,
        "type": "function",
        "function": {"name": "bash", "arguments": json.dumps({"command": call.command})},
    }


def price(model: str, input_tokens: int, output_tokens: int, cached_tokens: int = 0, cache_write_tokens: int = 0) -> float:
    """Returns the dollar cost of a call; raises KeyError for an unpriced model.

    `input_tokens` is the total prompt size; the cached and cache-write tokens
    are the parts of it billed at their own rates.
    """
    if model not in PRICES_PER_MILLION:
        raise KeyError(f"No price for {model!r}; add it to PRICES_PER_MILLION.")
    rates = PRICES_PER_MILLION[model]
    uncached = input_tokens - cached_tokens - cache_write_tokens
    total = (
        uncached * rates.input
        + cached_tokens * rates.cached_input
        + cache_write_tokens * rates.cache_write
        + output_tokens * rates.output
    )
    return total / 1_000_000


def to_responses_input(messages: list[dict]) -> tuple[str, list[dict]]:
    """Translates a chat-completions history into Responses API instructions and input items.

    The system message becomes the instructions. Each assistant turn expands into
    its reasoning items, its text and its function calls, in that order, and each
    tool message becomes the matching function-call output.
    """
    instructions, items = "", []
    for message in messages:
        role = message["role"]
        if role == "system":
            instructions = message["content"]
        elif role == "user":
            items.append({"role": "user", "content": message["content"]})
        elif role == "assistant":
            items.extend(message.get("reasoning", []))
            if message.get("content"):
                items.append({"role": "assistant", "content": message["content"]})
            for call in message.get("tool_calls", []):
                items.append({
                    "type": "function_call",
                    "call_id": call["id"],
                    "name": call["function"]["name"],
                    "arguments": call["function"]["arguments"],
                })
        elif role == "tool":
            items.append({"type": "function_call_output", "call_id": message["tool_call_id"], "output": message["content"]})
    return instructions, items


def from_responses_output(output: list) -> tuple[dict, list[ToolCall]]:
    """Folds Responses API output items back into one chat-completions assistant message."""
    texts, calls, reasoning = [], [], []
    for item in output:
        if item.type == "reasoning":
            # Without stored state, the encrypted reasoning is what lets the model
            # pick up its own chain of thought on the next turn.
            reasoning.append({
                "type": "reasoning",
                "id": item.id,
                "summary": [part.model_dump() for part in item.summary],
                "encrypted_content": item.encrypted_content,
            })
        elif item.type == "message":
            texts.extend(part.text for part in item.content if part.type == "output_text")
        elif item.type == "function_call":
            try:
                command = json.loads(item.arguments).get("command", "")
            except json.JSONDecodeError:
                command = item.arguments
            calls.append(ToolCall(id=item.call_id, command=command))
    message: dict = {"role": "assistant", "content": "\n".join(texts)}
    if calls:
        message["tool_calls"] = [tool_call_message(call) for call in calls]
    if reasoning:
        message["reasoning"] = reasoning
    return message, calls


class OpenAIClient:
    """Calls the OpenAI Responses API with a single bash tool and no stored state."""

    def __init__(self, model: str = DEFAULT_MODEL, reasoning_effort: str = REASONING_EFFORT):
        from openai import OpenAI

        price(model, 0, 0)  # Fails before the first call if the model has no price.
        self.model = model
        self.reasoning_effort = reasoning_effort
        self._client = OpenAI()

    def complete(self, messages: list[dict]) -> ModelReply:
        instructions, items = to_responses_input(messages)
        response = self._client.responses.create(
            model=self.model,
            instructions=instructions,
            input=items,
            tools=[BASH_TOOL],
            parallel_tool_calls=False,
            reasoning={"effort": self.reasoning_effort},
            store=False,
            include=["reasoning.encrypted_content"],
        )
        message, calls = from_responses_output(response.output)
        usage = response.usage
        details = usage.input_tokens_details
        cached, written = details.cached_tokens or 0, getattr(details, "cache_write_tokens", 0) or 0
        return ModelReply(
            message=message,
            tool_calls=calls,
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
            cost_usd=price(self.model, usage.input_tokens, usage.output_tokens, cached, written),
        )
