from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AuthRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=128)
    display_name: str | None = Field(default=None, max_length=100)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    player_id: int


class PlayerCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    display_name: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=6, max_length=128)


class PlayerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    display_name: str
    avatar: str | None = None


class NewGameRequest(BaseModel):
    difficulty: str = Field(default="easy", pattern="^(easy|medium|hard)$")


class BlockShape(BaseModel):
    id: str
    name: str
    cells: list[list[int]]
    color: str


class PlaceRequest(BaseModel):
    block_id: str
    row: int = Field(ge=0, lt=10)
    col: int = Field(ge=0, lt=10)


class SaveProgressRequest(BaseModel):
    board: list[list[int]]
    available_blocks: list[BlockShape]
    status: str = Field(default="active", pattern="^(active|paused|game_over)$")


class GameStatusResponse(BaseModel):
    id: int
    difficulty: str
    board: list[list[int]]
    available_blocks: list[BlockShape]
    score: int
    status: str
    moves: int
    cleared_lines: int


class LeaderboardEntry(BaseModel):
    rank: int
    player_id: int
    username: str
    display_name: str
    best_score: int


class HistoryEntry(BaseModel):
    id: int
    difficulty: str
    final_score: int
    moves: int
    cleared_lines: int
    completed: bool
    created_at: datetime


class StatisticsResponse(BaseModel):
    games_played: int
    total_score: int
    best_score: int
    total_moves: int
    total_cleared_lines: int
