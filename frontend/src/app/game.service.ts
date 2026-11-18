import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { GameStatus, HistoryEntry, LeaderboardEntry, Statistics } from './game.models';

@Injectable({ providedIn: 'root' })
export class GameService {
  private http = inject(HttpClient);
  private api = 'http://localhost:8000/api';
  token = typeof localStorage !== 'undefined' ? localStorage.getItem('token') ?? '' : '';

  private headers() {
    return { headers: new HttpHeaders({ Authorization: `Bearer ${this.token}` }) };
  }

  register(username: string, password: string, displayName: string) {
    return this.http.post<{ id: number }>(`${this.api}/players/register`, {
      username, password, display_name: displayName
    });
  }

  login(username: string, password: string) {
    return this.http.post<{ access_token: string; player_id: number }>(`${this.api}/players/login`, {
      username, password
    });
  }

  newGame(difficulty: 'easy' | 'medium' | 'hard'): Observable<GameStatus> {
    return this.http.post<GameStatus>(`${this.api}/games/new`, { difficulty }, this.headers());
  }

  place(sessionId: number, blockId: string, row: number, col: number): Observable<GameStatus> {
    return this.http.post<GameStatus>(`${this.api}/games/${sessionId}/place`, {
      block_id: blockId, row, col
    }, this.headers());
  }

  getStatus(sessionId: number): Observable<GameStatus> {
    return this.http.get<GameStatus>(`${this.api}/games/${sessionId}`, this.headers());
  }

  restart(sessionId: number): Observable<GameStatus> {
    return this.http.post<GameStatus>(`${this.api}/games/${sessionId}/restart`, {}, this.headers());
  }

  leaderboard(): Observable<LeaderboardEntry[]> {
    return this.http.get<LeaderboardEntry[]>(`${this.api}/games/leaderboard/all`);
  }

  history(): Observable<HistoryEntry[]> {
    return this.http.get<HistoryEntry[]>(`${this.api}/games/history/all`, this.headers());
  }

  statistics(): Observable<Statistics> {
    return this.http.get<Statistics>(`${this.api}/games/stats/all`, this.headers());
  }
}
