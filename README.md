---

![Block Blast Solver](https://raw.githubusercontent.com/radmin1337/Block-Blast-Solver/refs/heads/main/images/blockblastsolver.png)

---

# Block Blast Solver

A high-performance, AI-powered desktop application designed to solve puzzles in the popular game **Block Blast**. This tool uses a Depth First Search (DFS) algorithm combined with a custom heuristic evaluation function to find the most efficient sequence of moves for any given board state.

## Features

*   **Dark Mode Interface:** A sleek, distraction-free black and graphite UI.
*   **Real-time Progress Tracker:** A dedicated progress bar to monitor the AI's thinking process during complex calculations.
*   **Interactive 8x8 Board:** Mirror your game board by simply clicking on the cells.
*   **Shape Editors:** Draw your three current blocks in the mini-grid editors.
*   **Multi-threaded Solver:** The UI remains responsive while the AI calculates the best moves in the background.
*   **Visual Move Sequence:** Suggested moves are highlighted with a distinct color sequence:
    *   🟡 **Yellow:** First move.
    *   🟠 **Orange:** Second move.
    *   🔴 **Red:** Third move.
    *   ⚪ **White Dashed Border:** Clearly indicates where blocks overlap in the suggested sequence.

## Installation

### Prerequisites
*   Python 3.8 or higher
*   pip (Python package manager)

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/radmin1337/Block-Blast-Solver.git
   cd Block-Blast-Solver
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```

## How to Use

1.  **Set the Board:** Click on the main 8x8 grid to match the blocks currently on your screen.
2.  **Draw Shapes:** Use the three "SHAPE" editors at the bottom to draw the blocks you currently have.
3.  **Solve:** Click the **SOLVE** button. The progress bar will show the AI's calculation status.
4.  **Follow the Guide:** Once finished, the board will highlight the best moves. 
5.  **Apply:** Click **APPLY** to update the board state after you make the moves in your game, or click **CLEAR** to start a new round.

## The Algorithm

The solver simulates every possible permutation of the three shapes. It evaluates the resulting board states using a heuristic formula that considers:
*   **Line Clears:** Prioritizes clearing multiple rows and columns simultaneously.
*   **Board Density:** Keeps the board as empty as possible.
*   **Hole Penalty:** Penalizes moves that create isolated empty spaces.
*   **Preparation:** Favors leaving rows/columns at 6 or 7 blocks to set up for future combos.

---
  
