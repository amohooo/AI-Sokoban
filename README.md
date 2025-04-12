# Sokoban Puzzle Solver - Artificial Intelligence

This project implements a Sokoban puzzle solver using informed search techniques, specifically the A* search algorithm. The solver accounts for weighted boxes and aims to find the most cost-efficient sequence of actions to solve a given Sokoban warehouse layout.

## Project Description

This solver is designed to interact with the provided `search.py` and `sokoban.py` files. It adheres strictly to the defined interfaces and includes:

- **Taboo Cell Identification**: Implements corner and wall-based rules to mark cells as taboo (unsolvable if a box is pushed there).
- **SokobanPuzzle Class**: Extends `search.Problem` to model the Sokoban environment and actions.
- **Heuristic Function**: A domain-specific heuristic that includes:
  - Weighted Manhattan distance from boxes to targets
  - Worker distance to the nearest box
  - Penalties for placing boxes on taboo cells
- **Path Cost**: Considers both movement cost and box weight.
- **A* Search**: Utilizes informed search to efficiently find optimal or near-optimal solutions.

## Features

- `taboo_cells()`: Identifies cells that should be avoided for pushing boxes.
- `SokobanPuzzle`: Main problem class that supports action simulation, goal testing, and heuristic evaluation.
- `solve_weighted_sokoban()`: High-level function to compute the optimal action sequence and total cost.
- Action validation via `check_elem_action_seq()` and `check_each_action_and_move()`.

## Usage

1. Make sure the following files are in the same directory:
    - `search.py`
    - `sokoban.py`
    - Your Sokoban warehouse map file (e.g., `warehouse1.txt`)
2. Load and solve the puzzle:
```python
from sokoban import Warehouse
from my_sokoban import solve_weighted_sokoban

wh = Warehouse()
wh.load_warehouse("warehouse1.txt")

actions, cost = solve_weighted_sokoban(wh)
print("Solution:", actions)
print("Total Cost:", cost)

## Notes

Only legal moves are allowed (cannot push two boxes or push into walls).

The system penalizes pushing boxes into taboo cells, discouraging unsolvable states.

All interfaces comply with the requirements specified by the unit.

[<img src="\images\demo.gif">]


