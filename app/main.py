
"""FastAPI application for natural language sales analytics."""

import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.llm import generate_sql, LLMGenerationError
from app.sql_validator import SQLValidationError
from app.database import execute_query, DatabaseQueryError


logger = logging.getLogger(__name__)

app = FastAPI(
    title="Sales Analytics LLM API",
    description="Natural language analytics with Gemini and DuckDB.",
    version="0.2.0",
)


class QuestionRequest(BaseModel):
    question: str = Field(
        min_length=3,
        max_length=500,
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask")
def ask(request: QuestionRequest):
    """Generate, validate and execute an analytical SQL query."""

    try:
        # 1. Generate SQL using Gemini.
        sql = generate_sql(request.question)
        

        # 2. Validate and execute in read-only DuckDB.
        rows = execute_query(sql)

        # 3. Return real database results.
        return {
            "question": request.question,
            "sql": sql,
            "rows": rows,
            "row_count": len(rows),
        }

    except LLMGenerationError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    except SQLValidationError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Unsafe or invalid SQL: {exc}",
        ) from exc

    except DatabaseQueryError as exc:
        logger.warning("Database query rejected: %s", exc)
        raise HTTPException(
            status_code=400,
            detail="Generated SQL could not be executed.",
        ) from exc
