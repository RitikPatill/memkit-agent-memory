#!/usr/bin/env python3
"""Minimal chatbot that injects retrieved memories into each Anthropic API call.

Usage:
    ANTHROPIC_API_KEY=sk-... python examples/chatbot.py

Requires a running MemKit server (default: http://localhost:8000).
Type 'exit' to quit.
"""
from __future__ import annotations

import os

import anthropic

from memkit import MemKitClient

MEMKIT_URL = os.getenv("MEMKIT_URL", "http://localhost:8000")
MODEL = "claude-haiku-4-5-20251001"


def build_system_prompt(memories: list[dict]) -> str:
    if not memories:
        return "You are a helpful assistant."
    lines = "\n".join(f"- {m['text']}" for m in memories)
    return f"Relevant context from memory:\n{lines}\n\nYou are a helpful assistant."


def main() -> None:
    mem_client = MemKitClient(MEMKIT_URL)
    anthropic_client = anthropic.Anthropic()
    messages: list[dict] = []

    print("Chatbot ready. Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "exit":
            break
        if not user_input:
            continue

        memories = mem_client.search(user_input, k=3)
        system_prompt = build_system_prompt(memories)

        messages.append({"role": "user", "content": user_input})

        response = anthropic_client.messages.create(
            model=MODEL,
            max_tokens=512,
            system=system_prompt,
            messages=messages,
        )

        assistant_text = response.content[0].text
        messages.append({"role": "assistant", "content": assistant_text})
        print(f"Assistant: {assistant_text}\n")


if __name__ == "__main__":
    main()
