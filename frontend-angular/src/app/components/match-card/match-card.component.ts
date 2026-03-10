import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { ValueBetItem } from '../../models/match.interface';

@Component({
  selector: 'vb-match-card',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatButtonModule],
  templateUrl: './match-card.component.html',
  styleUrl: './match-card.component.scss'
})
export class MatchCardComponent {
  @Input() match!: ValueBetItem;
  @Input() highlight = false;
  @Output() select = new EventEmitter<ValueBetItem>();

  onClick(): void {
    this.select.emit(this.match);
  }
}
