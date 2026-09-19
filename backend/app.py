from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import json

from backend.services.ai_investigator import investigate_candidate

app = FastAPI(
    title="CleanMaster AI",
    description="Data cleanup and duplicate detection API",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5175",
        "http://127.0.0.1:5175"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5175",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# HOME
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "CleanMaster AI API is running",
        "status": "success"
    }


# --------------------------------------------------
# GET DUPLICATE RESULTS
# --------------------------------------------------

@app.get("/duplicates")
def get_duplicates():

    project_root = Path(__file__).resolve().parents[1]

    result_file = project_root / "data" / "candidate_results.json"

    if not result_file.exists():
        return {
            "status": "error",
            "message": "candidate_results.json not found"
        }

    with open(result_file, "r", encoding="utf-8") as file:
        candidates = json.load(file)

    return {
        "status": "success",
        "count": len(candidates),
        "candidates": candidates
    }


# --------------------------------------------------
# GET DECISION RESULTS
# --------------------------------------------------

@app.get("/decisions")
def get_decisions():

    project_root = Path(__file__).resolve().parents[1]

    result_file = project_root / "data" / "decision_results.json"

    if not result_file.exists():
        return {
            "status": "error",
            "message": "decision_results.json not found"
        }

    with open(result_file, "r", encoding="utf-8") as file:
        decisions = json.load(file)

    return {
        "status": "success",
        "count": len(decisions),
        "decisions": decisions
    }


# --------------------------------------------------
# AI INVESTIGATION REQUEST
# --------------------------------------------------

class InvestigationRequest(BaseModel):
    customer_1: str
    customer_2: str


@app.post("/investigate")
def investigate(request: InvestigationRequest):

    project_root = Path(__file__).resolve().parents[1]

    result_file = project_root / "data" / "candidate_results.json"

    if not result_file.exists():
        raise HTTPException(
            status_code=404,
            detail="candidate_results.json not found"
        )

    with open(result_file, "r", encoding="utf-8") as file:
        candidates = json.load(file)

    # Find requested customer pair
    selected_candidate = None

    for candidate in candidates:

        pair = {
            candidate.get("customer_1"),
            candidate.get("customer_2")
        }

        requested_pair = {
            request.customer_1,
            request.customer_2
        }

        if pair == requested_pair:
            selected_candidate = candidate
            break

    if selected_candidate is None:
        raise HTTPException(
            status_code=404,
            detail="Customer pair not found"
        )

    # Send candidate to Gemini AI Investigator
    result = investigate_candidate(selected_candidate)

    return {
        "status": "success",
        "investigation": result
    }