from app.services.game_engine import empty_board, can_place, place_block, random_blocks


def test_empty_board():
    board = empty_board()
    assert len(board) == 10
    assert all(len(row) == 10 for row in board)


def test_invalid_placement():
    board = empty_board()
    block = {"cells": [[0, 0], [0, 1]], "name": "line"}
    assert not can_place(board, block["cells"], 0, 9)


def test_block_placement_and_score():
    board = empty_board()
    block = {"cells": [[0, 0]], "name": "single"}
    updated, points, cleared = place_block(board, block, 5, 5)
    assert updated[5][5] == 1
    assert points == 1
    assert cleared == 0


def test_clear_complete_row():
    board = empty_board()
    board[0] = [1] * 10
    block = {"cells": [[0, 0]], "name": "single"}
    updated, points, cleared = place_block(board, block, 1, 0)
    assert cleared == 1
    assert points >= 101


def test_random_blocks():
    blocks = random_blocks(3)
    assert len(blocks) == 3
    assert len({block["id"] for block in blocks}) == 3
