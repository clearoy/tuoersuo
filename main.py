from src.config import DEFAULT_CONFIG
from src.run import run

if __name__ == "__main__":
    score = run(DEFAULT_CONFIG)
    total = DEFAULT_CONFIG.rows * DEFAULT_CONFIG.cols
    print(f"Game over. Cleared {score} of {total} cells.")
