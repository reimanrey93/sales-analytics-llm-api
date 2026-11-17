
"""Sales Analytics API."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.llm import generate_sql, LLMGenerationError


app = FastAPI(
    title="Sales Analytics LLM API",
    description="Natural language analytics powered by DuckDB.",
    version="0.1.0",
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
    try:
        sql = generate_sql(request.question)

        # SQL execution will be enabled only after
        # implementing security validation.
        return {
            "question": request.question,
            "sql": sql,
            "status": "pending_validation",
        }

    except LLMGenerationError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc
