"""The only file in this course that knows how to reach Chatterbox.

Read it. It is short on purpose. Everything else in the course is built
on top of these ten lines, and you should understand all of them.
"""
import os

from openai import OpenAI

BASE_URL = "https://chatterbox.ee.cooper.edu/api/v1"
MODEL = "nvidia/Gemma-4-26B-A4B-NVFP4"  # confirmed via /api/v1/models

client = OpenAI(base_url=BASE_URL, api_key=os.environ["CHATTERBOX_KEY"])


def chat(messages, temperature=0.7, **kw) -> str:
    """Send a list of {"role": ..., "content": ...} dicts, get a string back."""
    r = client.chat.completions.create(
        model=MODEL, messages=messages, temperature=temperature, **kw
    )
    return r.choices[0].message.content


if __name__ == "__main__":
    print(chat([{"role": "user", "content": "Say hello in exactly four words."}]))
