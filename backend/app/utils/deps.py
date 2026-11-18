from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.entities import Player
from app.utils.security import get_player_id


def get_current_player(authorization: str = Header(...), db: Session = Depends(get_db)) -> Player:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bearer token required")
    try:
        player_id = get_player_id(authorization.removeprefix("Bearer ").strip())
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    player = db.get(Player, player_id)
    if player is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Player not found")
    return player
