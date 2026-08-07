import sys
import itertools
import copy
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QGridLayout,
    QVBoxLayout, QHBoxLayout, QMessageBox, QProgressBar, QLabel
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

SIZE = 8

def can_place(board, shape, x, y):
    for dx, dy in shape:
        nx, ny = x + dx, y + dy
        if nx < 0 or ny < 0 or nx >= SIZE or ny >= SIZE:
            return False
        if board[nx][ny] == 1:
            return False
    return True

def clear_lines(board):
    new = copy.deepcopy(board)
    full_rows = [i for i in range(SIZE) if all(new[i][j] for j in range(SIZE))]
    full_cols = [j for j in range(SIZE) if all(new[i][j] for i in range(SIZE))]
    
    for i in full_rows:
        for j in range(SIZE): new[i][j] = 0
    for j in full_cols:
        for i in range(SIZE): new[i][j] = 0
        
    return new, len(full_rows) + len(full_cols)

def place(board, shape, x, y):
    new_board = copy.deepcopy(board)
    for dx, dy in shape:
        new_board[x + dx][y + dy] = 1
    return clear_lines(new_board)

def get_moves(board, shape):
    return [(x, y) for x in range(SIZE) for y in range(SIZE) if can_place(board, shape, x, y)]

def evaluate(board, total_cleared):
    filled = sum(sum(r) for r in board)
    near_lines = 0
    for i in range(SIZE):
        if sum(board[i]) >= SIZE - 2: near_lines += 1
        if sum(board[j][i] for j in range(SIZE)) >= SIZE - 2: near_lines += 1

    holes = 0
    for i in range(SIZE):
        for j in range(SIZE):
            if board[i][j] == 0:
                neighbors = sum(1 for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]
                              if 0 <= i+dx < SIZE and 0 <= j+dy < SIZE and board[i+dx][j+dy] == 1)
                if neighbors >= 3: holes += 1

    height_penalty = sum(max([SIZE - i for i in range(SIZE) if board[i][j]] + [0]) for j in range(SIZE))
    return (total_cleared * 100 + near_lines * 10 - holes * 15 - filled * 2 - height_penalty)

class SolverThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(list)

    def __init__(self, board, shapes):
        super().__init__()
        self.board = board
        self.shapes = shapes

    def run(self):
        best_score = -999999
        best_seq = None
        perms = list(itertools.permutations(self.shapes))
        
        for p_idx, order in enumerate(perms):
            def dfs(b, i, path, cleared_total):
                nonlocal best_score, best_seq
                if i == 3:
                    score = evaluate(b, cleared_total)
                    if score > best_score:
                        best_score, best_seq = score, path
                    return
                
                moves = get_moves(b, order[i])
                if not moves: return
                for move in moves:
                    new_b, cleared = place(b, order[i], move[0], move[1])
                    dfs(new_b, i + 1, path + [(order[i], move)], cleared_total + cleared)

            dfs(self.board, 0, [], 0)
            self.progress.emit(int(((p_idx + 1) / len(perms)) * 100))
        
        self.finished.emit(best_seq if best_seq else [])

class ShapeEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.grid = [[0]*5 for _ in range(5)]
        layout = QGridLayout()
        layout.setSpacing(2)
        layout.setContentsMargins(0, 0, 0, 0)
        self.buttons = []
        for i in range(5):
            row = []
            for j in range(5):
                btn = QPushButton()
                btn.setFixedSize(28, 28)
                btn.clicked.connect(lambda _, x=i, y=j: self.toggle(x, y))
                layout.addWidget(btn, i, j)
                row.append(btn)
            self.buttons.append(row)
        self.setLayout(layout)
        self.update_ui()

    def toggle(self, x, y):
        self.grid[x][y] ^= 1
        self.update_ui()

    def update_ui(self):
        for i in range(5):
            for j in range(5):
                color = "#2ecc71" if self.grid[i][j] else "#2d2d2d"
                self.buttons[i][j].setStyleSheet(f"background: {color}; border: 1px solid #121212; border-radius: 0px;")

    def get_shape(self):
        cells = [(i, j) for i in range(5) for j in range(5) if self.grid[i][j]]
        if not cells: return None
        min_x, min_y = min(c[0] for c in cells), min(c[1] for c in cells)
        return [(x - min_x, y - min_y) for x, y in cells]

    def clear(self):
        self.grid = [[0]*5 for _ in range(5)]
        self.update_ui()

class CellButton(QPushButton):
    def __init__(self, x, y, app):
        super().__init__()
        self.x, self.y, self.app = x, y, app
        self.setFixedSize(50, 50)
        self.update_color()

    def mousePressEvent(self, event):
        self.app.board[self.x][self.y] ^= 1
        self.app.best_sequence = None
        self.app.update_grid()

    def update_color(self):
        val = self.app.board[self.x][self.y]
        bg_color = "#2d2d2d"
        border = "1px solid #121212"

        if val: bg_color = "#3498db"

        if self.app.best_sequence:
            last_touch, touch_count = None, 0
            for i, (shape, (sx, sy)) in enumerate(self.app.best_sequence):
                for dx, dy in shape:
                    if self.x == sx + dx and self.y == sy + dy:
                        last_touch, touch_count = i, touch_count + 1

            colors = ["#f9e79f", "#f5cba7", "#f5b7b1"]
            brd_colors = ["#f1c40f", "#e67e22", "#e74c3c"]
            
            if touch_count > 1:
                bg_color = colors[last_touch]
                border = "2px dashed #ffffff"
            elif touch_count == 1:
                bg_color = colors[last_touch]
                border = f"3px solid {brd_colors[last_touch]}"

        self.setStyleSheet(f"background-color: {bg_color}; border: {border}; border-radius: 0px;")

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Block Blast Solver AI")
        self.board = [[0] * SIZE for _ in range(SIZE)]
        self.best_sequence = None
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QWidget { background-color: #000000; color: #ffffff; font-family: 'Segoe UI', Arial; }
            QPushButton { background-color: #1e1e1e; border: 1px solid #333; border-radius: 0px; color: #fff; font-size: 13px; font-weight: bold; }
            QPushButton:hover { background-color: #333; }
            QLabel { font-size: 11px; color: #888; font-weight: bold; }
            QProgressBar { border: 1px solid #333; background: #1e1e1e; height: 10px; text-align: center; color: white; font-size: 8px; border-radius: 0px; }
            QProgressBar::chunk { background-color: #27ae60; border-radius: 0px; }
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)

        grid_container = QGridLayout()
        grid_container.setSpacing(2)
        grid_container.setContentsMargins(0, 0, 0, 0)
        self.cells = []
        for i in range(SIZE):
            row = []
            for j in range(SIZE):
                btn = CellButton(i, j, self)
                grid_container.addWidget(btn, i, j)
                row.append(btn)
            self.cells.append(row)
        
        board_h_layout = QHBoxLayout()
        board_h_layout.addStretch()
        board_h_layout.addLayout(grid_container)
        board_h_layout.addStretch()
        main_layout.addLayout(board_h_layout)

        shapes_outer_layout = QHBoxLayout()
        shapes_outer_layout.setSpacing(20)
        self.editors = []
        for i in range(3):
            v_block = QVBoxLayout()
            v_block.setAlignment(Qt.AlignCenter)
            label = QLabel(f"SHAPE {i+1}")
            label.setAlignment(Qt.AlignCenter)
            v_block.addWidget(label)
            ed = ShapeEditor()
            v_block.addWidget(ed)
            shapes_outer_layout.addLayout(v_block)
            self.editors.append(ed)
        main_layout.addLayout(shapes_outer_layout)

        controls = QHBoxLayout()
        controls.setSpacing(8)
        
        self.solve_btn = QPushButton("SOLVE")
        self.solve_btn.setFixedHeight(40)
        self.solve_btn.clicked.connect(self.solve)
        
        self.apply_btn = QPushButton("APPLY")
        self.apply_btn.setFixedHeight(40)
        self.apply_btn.clicked.connect(self.apply_move)
        
        self.clear_btn = QPushButton("CLEAR")
        self.clear_btn.setFixedHeight(40)
        self.clear_btn.clicked.connect(self.clear)
        
        controls.addWidget(self.solve_btn)
        controls.addWidget(self.apply_btn)
        controls.addWidget(self.clear_btn)
        main_layout.addLayout(controls)

        self.setLayout(main_layout)
        self.setFixedSize(self.sizeHint())

    def update_grid(self):
        for i in range(SIZE):
            for j in range(SIZE): self.cells[i][j].update_color()

    def clear(self):
        self.board = [[0]*SIZE for _ in range(SIZE)]
        self.best_sequence = None
        for e in self.editors: e.clear()
        self.progress_bar.setValue(0)
        self.update_grid()

    def solve(self):
        shapes = []
        for e in self.editors:
            s = e.get_shape()
            if not s:
                QMessageBox.warning(self, "Error", "Define all 3 shapes first!")
                return
            shapes.append(s)

        self.solve_btn.setEnabled(False)
        self.solve_btn.setText("SOLVING...")
        
        self.thread = SolverThread(self.board, shapes)
        self.thread.progress.connect(self.progress_bar.setValue)
        self.thread.finished.connect(self.on_finished)
        self.thread.start()

    def on_finished(self, result):
        self.solve_btn.setEnabled(True)
        self.solve_btn.setText("SOLVE")
        
        if not result:
            QMessageBox.critical(self, "Failed", "No valid moves found.")
            return
        
        self.best_sequence = result
        self.update_grid()

    def apply_move(self):
        if not self.best_sequence:
            return
        
        temp = copy.deepcopy(self.board)
        for shape, (x, y) in self.best_sequence:
            temp, _ = place(temp, shape, x, y)
        
        self.board = temp
        self.best_sequence = None
        self.progress_bar.setValue(0)
        for e in self.editors: e.clear()
        self.update_grid()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec_())
