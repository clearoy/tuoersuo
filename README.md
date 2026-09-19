# ToBeCollege

基于OCR和OCV的开局托儿所破解

## Layout

```
src/
  config.py           settings (window title, board size, Gemini key/model via .env)
  run.py              assembles the four pipeline steps into capture -> OCR -> solve loop -> play
  pipeline/
    capture.py        finds the game window, screenshots + crops it, computes each cell's
                        pixel position (no per-tile image cropping - see below)
    ocr.py             sends the whole board image to Gemini in one call, gets back the
                        full digit grid as JSON
    solve.py            Board (digit grid + queries) + Solver interface + Move;
                        GreedySolver is the current strategy
    execute.py          turns a Move into a real click+drag on the game window
tests/                solve.py tests that don't need the real game running
main.py               entry point
```

Digit recognition reads the entire board in a single Gemini call instead of OCR-ing 160
individual tile crops, so `capture.py` only computes cell *geometry* (used later by
`execute.py` for click targeting) - it no longer crops/inverts/saves per-tile images.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in GEMINI_API_KEY (get one at https://aistudio.google.com/apikey)
```

On macOS, `pyautogui`'s screenshot/mouse control requires granting your terminal
Screen Recording and Accessibility permissions in System Settings > Privacy & Security.

## Run

```bash
python prerun.py   # captures the window, measures the board, saves calibration.json
python main.py
```

Re-run `prerun.py` whenever the game window's size or position changes.

## Test

```bash
pytest
```

## Choosing a solver

Set `SOLVER` in `.env` (or `Config.solver`) to one of:

- `greedy`: first sum-10 rectangle in scan order, pairs preferred at first.
- `smallest`: always the sum-10 rectangle that clears the fewest cells.
- `beam` (default): plans the whole game with beam search (`Config.beam_width`,
  `Config.beam_branching`); a wider beam plays better but takes longer before the first move.

## Swapping in a different solver

Everything upstream of solving (capture, OCR) and downstream (execute) stays the
same. To plug in a new strategy (e.g. an RL model), implement
`Solver.next_move(board) -> Move | None` in `src/pipeline/solve.py` and pass an
instance to `src.run.run(config, solver=YourSolver())`.
