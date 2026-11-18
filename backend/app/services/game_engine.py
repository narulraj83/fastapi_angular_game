import random

BOARD_SIZE = 10

SHAPES = [
    ("single", [[0, 0]], "#6C5CE7"),
    ("square", [[0, 0], [0, 1], [1, 0], [1, 1]], "#00CEC9"),
    ("line_h3", [[0, 0], [0, 1], [0, 2]], "#0984E3"),
    ("line_h5", [[0, 0], [0, 1], [0, 2], [0, 3], [0, 4]], "#0984E3"),
    ("line_v3", [[0, 0], [1, 0], [2, 0]], "#FDCB6E"),
    ("line_v5", [[0, 0], [1, 0], [2, 0], [3, 0], [4, 0]], "#FDCB6E"),
    ("l", [[0, 0], [1, 0], [2, 0], [2, 1]], "#E17055"),
    ("l_mirror", [[0, 1], [1, 1], [2, 1], [2, 0]], "#E17055"),
    ("t", [[0, 0], [0, 1], [0, 2], [1, 1]], "#E84393"),
    ("zigzag", [[0, 0], [0, 1], [1, 1], [1, 2]], "#00B894"),
]


def empty_board() -> list[list[int]]:
    return [[0] * BOARD_SIZE for _ in range(BOARD_SIZE)]


def random_blocks(count: int = 3, difficulty: str = "easy") -> list[dict]:
    pool = SHAPES if difficulty == "easy" else (SHAPES + [
        ("large_square", [[r, c] for r in range(3) for c in range(3)], "#A29BFE")
    ])
    blocks = []
    for _ in range(count):
        name, cells, color = random.choice(pool)
        blocks.append({
            "id": f"{name}-{random.randrange(1_000_000)}",
            "name": name,
            "cells": cells,
            "color": color,
        })
    return blocks


def can_place(board: list[list[int]], cells: list[list[int]], row: int, col: int) -> bool:
    for dr, dc in cells:
        r, c = row + dr, col + dc
        if r < 0 or c < 0 or r >= BOARD_SIZE or c >= BOARD_SIZE:
            return False
        if board[r][c] != 0:
            return False
    return True


def place_block(board: list[list[int]], block: dict, row: int, col: int) -> tuple[list[list[int]], int, int]:
    if not can_place(board, block["cells"], row, col):
        raise ValueError("Block does not fit at that position")

    updated = [line[:] for line in board]
    for dr, dc in block["cells"]:
        updated[row + dr][col + dc] = 1

    full_rows = [r for r in range(BOARD_SIZE) if all(updated[r])]
    full_cols = [c for c in range(BOARD_SIZE) if all(updated[r][c] for r in range(BOARD_SIZE))]

    for r in full_rows:
        updated[r] = [0] * BOARD_SIZE
    for c in full_cols:
        for r in range(BOARD_SIZE):
            updated[r][c] = 0

    cleared = len(full_rows) + len(full_cols)
    block_points = len(block["cells"])
    line_points = cleared * 100
    combo_bonus = (cleared * (cleared - 1) // 2) * 50 if cleared > 1 else 0
    return updated, block_points + line_points + combo_bonus, cleared


def has_available_move(board: list[list[int]], blocks: list[dict]) -> bool:
    for block in blocks:
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if can_place(board, block["cells"], row, col):
                    return True
    return False
