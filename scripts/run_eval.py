import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from backend.evaluation.run_eval import run_evaluation

if __name__ == "__main__":
    run_evaluation()
