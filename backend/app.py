from fastapi import FastAPI
from pathlib import Path
import json

app = FastAPI(
    title="CleanMaster AI",
    description="Data cleanup and duplicate detection API",
    version="1.0.0"
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