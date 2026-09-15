# ToBeCollege

基于OCR和OCV的开局托儿所破解

## Layout

```
src/
  config.py           settings (window title, board size, OCR keys via .env)
  run.py              assembles the four pipeline steps into capture -> OCR -> solve loop -> play
  pipeline/
    capture.py        finds the game window, screenshots + crops + slices it into Tiles
    ocr.py             Baidu OCR wrapper, reads every Tile's digit
    solve.py            Board (digit grid + queries) + Solver interface + Move;
                        GreedySolver is the current strategy
    execute.py          turns a Move into a real click+drag on the game window
tests/                solve.py tests that don't need the real game running
main.py               entry point
```

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in BAIDU_API_KEY / BAIDU_SECRET_KEY
```

On macOS, `pyautogui`'s screenshot/mouse control requires granting your terminal
Screen Recording and Accessibility permissions in System Settings > Privacy & Security.

## Run

```bash
python main.py
```

## Test

```bash
pytest
```

## Swapping in a different solver

Everything upstream of solving (capture, OCR) and downstream (execute) stays the
same. To plug in a new strategy (e.g. an RL model), implement
`Solver.next_move(board) -> Move | None` in `src/pipeline/solve.py` and pass an
instance to `src.run.run(config, solver=YourSolver())`.
