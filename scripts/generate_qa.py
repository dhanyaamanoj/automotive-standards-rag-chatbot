import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from backend.evaluation.synthetic_qa import generate_qa

if __name__ == "__main__":
    generate_qa()
