
"""Gemini integration for natural-language-to-SQL."""
import logging

logger = logging.getLogger(__name__)

import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


class LLMGenerationError(Exception):
    """Raised when SQL generation fails."""


SYSTEM_PROMPT = """
You are an expert DuckDB SQL analyst.

Convert natural language questions into SQL.

Allowed relations:

pedidos(
    fecha,
    cliente,
    pais,
    producto,
    importe,
    estado
)

ventas_mensuales_pais(
    mes,
    pais,
    total_pedidos,
    ventas_totales
)

top_10_clientes(
    cliente,
    total_pedidos,
    total_comprado
)

Rules:
- Return exactly one SQL SELECT query.
- Only use the allowed relations and columns.
- Never generate INSERT, UPDATE, DELETE or DDL.
- Only completed orders count as revenue.
- Use DuckDB-compatible SQL.
- Do not invent years or missing information.
- Return SQL only, without explanations or markdown.
"""


def generate_sql(question: str) -> str:
    """Generate a candidate SQL query using Gemini."""

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise LLMGenerationError(
            "GEMINI_API_KEY is not configured."
        )

    try:
        with genai.Client(api_key=api_key) as client:
            response = client.models.generate_content(
                model=os.getenv(
                    "GEMINI_MODEL",
                    "gemini-3.8-flash"
                ),
                contents=question,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0,
                    max_output_tokens=2048,
                ),
            )

        sql = (response.text or "").strip()
        
        candidate = (
            response.candidates[0]
            if response.candidates
            else None
        )

        if candidate is None:
            raise LLMGenerationError(
                "Gemini returned no candidate."
            )

        if candidate.finish_reason != types.FinishReason.STOP:
            raise LLMGenerationError(
                "Gemini did not finish generating SQL."
            )

        if not sql:
            raise LLMGenerationError(
                "Gemini returned an empty response."
            )

        return sql

    except LLMGenerationError:
        raise

    except Exception as exc:
        logger.exception(
            "Gemini SQL generation failed: %s",
            type(exc).__name__,
        )
        raise LLMGenerationError(
            "Gemini SQL generation failed."
        ) from exc