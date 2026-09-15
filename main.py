from src.config import DEFAULT_CONFIG
from src.pipeline import run

if __name__ == "__main__":
    score = run(DEFAULT_CONFIG)
    print(f"游戏结束，本次得分为{score}")
