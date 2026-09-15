# ToBeCollege

基于OCR和OCV的开局托儿所破解

## Layout

```
src/
  config.py          settings (window title, board size, OCR keys via .env)
  capture.py         finds the game window, screenshots + crops the board
  image_processor.py splits the screenshot into a rows x cols grid of Tiles
  ocr.py             Baidu OCR wrapper, reads the digit off one tile
  board.py           digit grid: rectangle sum/count queries, clearing
  solver.py          Solver interface + Move; GreedySolver is the current strategy
  controller.py      turns a Move into a real click+drag on the game window
  pipeline.py         wires the above into capture -> OCR -> solve loop -> play
tests/               solver/board tests that don't need the real game running
main.py              entry point
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

Everything upstream of solving (capture, OCR, board state) and downstream (mouse
control) stays the same. To plug in a new strategy (e.g. an RL model), implement
`Solver.next_move(board) -> Move | None` in `src/solver.py` and pass an instance to
`pipeline.run(config, solver=YourSolver())`.
