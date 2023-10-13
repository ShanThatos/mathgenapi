from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from mathgen import MathGenCode, MathProblemGenerator
from pydantic import BaseModel

from . import config, db, responses, utils

app = FastAPI()


@app.middleware("http")
async def require_api_token(request: Request, call_next):
    if config.ENVIRONMENT == "prod":
        if request.headers.get("Authorization") not in config.API_TOKENS:
            return JSONResponse(responses.error("Invalid API token"), status_code=401)
    return await call_next(request)


@app.post("/reset")
async def reset_db():
    db.rebuild_db()
    return responses.success()


class GenerateRequest(BaseModel):
    num: int = 1
    seed: Optional[int] = None


class GenerateModelRequest(GenerateRequest):
    model: str


class GenerateCodeRequest(GenerateRequest):
    code: MathGenCode


@app.post("/generate/model")
async def generate_from_model(gen: GenerateModelRequest):
    model, error = db.get_model(gen.model)
    if error or model is None:
        return responses.error(error)

    return responses.success(
        MathProblemGenerator.from_model(model, seed=gen.seed).generate_multiple(gen.num)
    )


@app.post("/generate/code")
async def generate_from_code(gen: GenerateCodeRequest):
    return responses.success(
        MathProblemGenerator(
            "generated_from_code", gen.code, seed=gen.seed
        ).generate_multiple(gen.num)
    )
