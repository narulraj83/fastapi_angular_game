from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.entities import Leaderboard, Player
from app.schemas.game import AuthRequest, PlayerCreate, PlayerResponse, TokenResponse
from app.utils.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/api/players", tags=["players"])


@router.post("/register", response_model=PlayerResponse, status_code=201)
def register(payload: PlayerCreate, db: Session = Depends(get_db)):
    exists = db.scalar(select(Player).where(Player.username == payload.username.lower()))
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")
    player = Player(username=payload.username.lower(), display_name=payload.display_name,
                    password_hash=hash_password(payload.password))
    db.add(player)
    db.flush()
    db.add(Leaderboard(player_id=player.id, best_score=0))
    db.commit()
    db.refresh(player)
    return player


@router.post("/login", response_model=TokenResponse)
def login(payload: AuthRequest, db: Session = Depends(get_db)):
    player = db.scalar(select(Player).where(Player.username == payload.username.lower()))
    if player is None or not verify_password(payload.password, player.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return TokenResponse(access_token=create_access_token(player.id), player_id=player.id)
