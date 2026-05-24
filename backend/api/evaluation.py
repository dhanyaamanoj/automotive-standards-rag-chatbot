import json, os
from fastapi import APIRouter, BackgroundTasks

router = APIRouter()
RESULTS_PATH = "backend/data/eval_results.json"

@router.get("/evaluation/results")
def get_results():
    if not os.path.exists(RESULTS_PATH):
        return {"message": "No evaluation results yet. Run POST /api/evaluation/run"}
    with open(RESULTS_PATH) as f:
        return json.load(f)

@router.post("/evaluation/run")
def run_evaluation(bg: BackgroundTasks):
    def _run():
        from backend.evaluation.run_eval import run_evaluation
        run_evaluation()
    bg.add_task(_run)
    return {"status": "Evaluation started in background"}
