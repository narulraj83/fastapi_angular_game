import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.entities import GameHistory, GameScore, GameSession, Leaderboard, Player
from app.schemas.game import (GameStatusResponse, HistoryEntry, LeaderboardEntry,
                              NewGameRequest, PlaceRequest, SaveProgressRequest,
                              StatisticsResponse)
from app.services.game_engine import (empty_board, has_available_move, place_block,
                                      random_blocks)
from app.utils.deps import get_current_player

router = APIRouter(prefix="/api/games", tags=["games"])


def session_response(session: GameSession) -> GameStatusResponse:
    return GameStatusResponse(
        id=session.id, difficulty=session.difficulty,
        board=json.loads(session.board), available_blocks=json.loads(session.available_blocks),
        score=session.score, status=session.status, moves=session.moves,
        cleared_lines=session.cleared_lines,
    )


def get_session(db: Session, session_id: int, player: Player) -> GameSession:
    session = db.get(GameSession, session_id)
    if session is None or session.player_id != player.id:
        raise HTTPException(status_code=404, detail="Game session not found")
    return session


@router.post("/new", response_model=GameStatusResponse)
def new_game(payload: NewGameRequest, db: Session = Depends(get_db),
             player: Player = Depends(get_current_player)):
    session = GameSession(player_id=player.id, difficulty=payload.difficulty,
                          board=json.dumps(empty_board()),
                          available_blocks=json.dumps(random_blocks(3, payload.difficulty)))
    db.add(session)
    db.commit()
    db.refresh(session)
    return session_response(session)


@router.post("/{session_id}/place", response_model=GameStatusResponse)
def place(session_id: int, payload: PlaceRequest, db: Session = Depends(get_db),
          player: Player = Depends(get_current_player)):
    session = get_session(db, session_id, player)
    if session.status == "game_over":
        raise HTTPException(status_code=409, detail="Game is already over")

    board = json.loads(session.board)
    blocks = json.loads(session.available_blocks)
    block = next((item for item in blocks if item["id"] == payload.block_id), None)
    if block is None:
        raise HTTPException(status_code=400, detail="Block is not available")

    try:
        updated, points, cleared = place_block(board, block, payload.row, payload.col)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    remaining = [item for item in blocks if item["id"] != payload.block_id]
    if not remaining:
        remaining = random_blocks(3, session.difficulty)

    session.board = json.dumps(updated)
    session.available_blocks = json.dumps(remaining)
    session.score += points
    session.moves += 1
    session.cleared_lines += cleared

    if not has_available_move(updated, remaining):
        session.status = "game_over"
        finalize_history(db, session)

    db.flush()
    _update_scores(db, session)
    db.commit()
    db.refresh(session)
    return session_response(session)


def finalize_history(db: Session, session: GameSession) -> None:
    existing = db.scalar(select(GameHistory).where(GameHistory.session_id == session.id))
    if existing is None:
        db.add(GameHistory(player_id=session.player_id, session_id=session.id,
                           difficulty=session.difficulty, final_score=session.score,
                           moves=session.moves, cleared_lines=session.cleared_lines, completed=True))


def _update_scores(db: Session, session: GameSession) -> None:
    score_row = db.scalar(select(GameScore).where(GameScore.session_id == session.id))
    if score_row is None:
        db.add(GameScore(player_id=session.player_id, session_id=session.id, score=session.score))
    else:
        score_row.score = session.score

    leaderboard = db.scalar(select(Leaderboard).where(Leaderboard.player_id == session.player_id))
    if leaderboard is None:
        db.add(Leaderboard(player_id=session.player_id, best_score=session.score))
    elif session.score > leaderboard.best_score:
        leaderboard.best_score = session.score


@router.get("/{session_id}", response_model=GameStatusResponse)
def get_status(session_id: int, db: Session = Depends(get_db),
               player: Player = Depends(get_current_player)):
    return session_response(get_session(db, session_id, player))


@router.put("/{session_id}/progress", response_model=GameStatusResponse)
def save_progress(session_id: int, payload: SaveProgressRequest, db: Session = Depends(get_db),
                  player: Player = Depends(get_current_player)):
    session = get_session(db, session_id, player)
    if len(payload.board) != 10 or any(len(row) != 10 for row in payload.board):
        raise HTTPException(status_code=400, detail="Board must be 10 by 10")
    session.board = json.dumps(payload.board)
    session.available_blocks = json.dumps([block.model_dump() for block in payload.available_blocks])
    session.status = payload.status
    db.flush()
    _update_scores(db, session)
    if payload.status == "game_over":
        finalize_history(db, session)
    db.commit()
    db.refresh(session)
    return session_response(session)


@router.post("/{session_id}/restart", response_model=GameStatusResponse)
def restart_game(session_id: int, db: Session = Depends(get_db),
                 player: Player = Depends(get_current_player)):
    session = get_session(db, session_id, player)
    session.board = json.dumps(empty_board())
    session.available_blocks = json.dumps(random_blocks(3, session.difficulty))
    session.score = 0
    session.status = "active"
    session.moves = 0
    session.cleared_lines = 0
    db.flush()
    _update_scores(db, session)
    db.commit()
    db.refresh(session)
    return session_response(session)


@router.get("/leaderboard/all", response_model=list[LeaderboardEntry])
def leaderboard(limit: int = 20, db: Session = Depends(get_db)):
    rows = db.execute(select(Leaderboard, Player).join(Player, Player.id == Leaderboard.player_id)
                      .order_by(desc(Leaderboard.best_score)).limit(limit)).all()
    return [LeaderboardEntry(rank=index, player_id=player.id, username=player.username,
                             display_name=player.display_name, best_score=row.best_score)
            for index, (row, player) in enumerate(rows, start=1)]


@router.get("/history/all", response_model=list[HistoryEntry])
def history(limit: int = 50, db: Session = Depends(get_db),
            player: Player = Depends(get_current_player)):
    rows = db.scalars(select(GameHistory).where(GameHistory.player_id == player.id)
                      .order_by(desc(GameHistory.created_at)).limit(limit)).all()
    return rows


@router.get("/stats/all", response_model=StatisticsResponse)
def statistics(db: Session = Depends(get_db), player: Player = Depends(get_current_player)):
    rows = db.scalars(select(GameHistory).where(GameHistory.player_id == player.id)).all()
    leaderboard = db.scalar(select(Leaderboard).where(Leaderboard.player_id == player.id))
    return StatisticsResponse(
        games_played=len(rows),
        total_score=sum(row.final_score for row in rows),
        best_score=leaderboard.best_score if leaderboard else 0,
        total_moves=sum(row.moves for row in rows),
        total_cleared_lines=sum(row.cleared_lines for row in rows),
    )
