import { Component } from '@angular/core';
import { GameComponent } from './game.component';

@Component({
  selector: 'app-root',
  imports: [GameComponent],
  template: '<app-game />',
})
export class App {}
