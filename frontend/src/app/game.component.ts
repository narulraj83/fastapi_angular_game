import { Component, inject, PLATFORM_ID, OnInit } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { GameService } from './game.service';
import { BlockShape, GameStatus, LeaderboardEntry } from './game.models';

@Component({
  selector: 'app-game',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './game.component.html',
  styleUrl: './game.component.css',
})
export class GameComponent implements OnInit {
  private readonly game = inject(GameService);
  private readonly platformId = inject(PLATFORM_ID);
  gameState: GameStatus | null = null;
  leaderboard: LeaderboardEntry[] = [];
  selected: BlockShape | null = null;
  hoverRow = -1;
  hoverCol = -1;
  difficulty: 'easy' | 'medium' | 'hard' = 'easy';
  username = '';
  password = '';
  displayName = '';
  loggedIn = false;
  dark = false;
  paused = false;
  authError = '';

  ngOnInit() {
    if (!isPlatformBrowser(this.platformId)) return;
    if (this.game.token) this.loggedIn = true;
    this.loadLeaderboard();
  }

  login() {
    if (!this.username || this.password.length < 6) {
      this.authError = 'Enter a username and password with at least 6 characters.';
      return;
    }
    this.authError = '';
    this.game.login(this.username, this.password).subscribe({
      next: result => {
        localStorage.setItem('token', result.access_token);
        this.game.token = result.access_token;
        this.loggedIn = true;
      },
      error: error => {
        if (error.status === 401) {
          this.register();
        } else {
          this.authError = error.error?.detail || 'Unable to connect to the game server.';
        }
      },
    });
  }

  register() {
    this.game.register(this.username, this.password, this.displayName || this.username).subscribe({
      next: () => this.login(),
      error: error => {
        if (error.status === 409) {
          this.authError = 'That username exists. Enter the correct password.';
        } else {
          this.authError = error.error?.detail || 'Unable to create the player account.';
        }
      },
    });
  }

  start() {
    if (!this.loggedIn) return;
    this.game.newGame(this.difficulty).subscribe(result => this.gameState = result);
  }

  selectBlock(block: BlockShape) {
    this.selected = block;
  }

  preview(row: number, col: number) {
    this.hoverRow = row;
    this.hoverCol = col;
  }

  isPreview(row: number, col: number) {
    if (!this.selected || this.hoverRow < 0) return false;
    return this.selected.cells.some(([dr, dc]) => row === this.hoverRow + dr && col === this.hoverCol + dc);
  }

  place(row: number, col: number) {
    if (!this.selected || !this.gameState || this.paused) return;
    this.game.place(this.gameState.id, this.selected.id, row, col).subscribe({
      next: result => {
        this.gameState = result;
        this.selected = null;
        this.hoverRow = -1;
        this.hoverCol = -1;
      },
      error: err => alert(err.error?.detail || 'The block cannot be placed here'),
    });
  }

  restart() {
    if (!this.gameState) return;
    this.game.restart(this.gameState.id).subscribe(result => {
      this.gameState = result;
      this.selected = null;
      this.paused = false;
    });
  }

  togglePause() {
    this.paused = !this.paused;
  }

  loadLeaderboard() {
    this.game.leaderboard().subscribe(result => this.leaderboard = result);
  }

  toggleTheme() {
    this.dark = !this.dark;
  }
}
