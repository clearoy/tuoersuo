"""Step 2: read the whole board's digit grid in a single Gemini call.

One multimodal call replaces the old per-tile loop entirely - no tile images needed.
"""

import json

from google import genai
from google.genai import types

_PROMPT_TEMPLATE = (
    "This image shows a {rows}x{cols} grid of numbered tiles from a puzzle game. "
    "Read it top-to-bottom, left-to-right. Each cell contains a single digit 1-9. "
    "Return ONLY a JSON array of exactly {count} integers, one per cell, in row-major "
    "order (all of row 1 left-to-right, then all of row 2, and so on). No other text."
)


def recognize_board(image_path: str, rows: int, cols: int, api_key: str, model: str) -> list:
    if not api_key:
        raise ValueError("Gemini API key is not configured")

    client = genai.Client(api_key=api_key)

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    prompt = _PROMPT_TEMPLATE.format(rows=rows, cols=cols, count=rows * cols)

    response = client.models.generate_content(
        model=model,
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
            prompt,
        ],
        config=types.GenerateContentConfig(response_mime_type="application/json"),
    )

    digits = json.loads(response.text)
    if len(digits) != rows * cols:
        raise ValueError(f"Gemini returned {len(digits)} digits, expected {rows * cols}")
    return [int(d) for d in digits]
