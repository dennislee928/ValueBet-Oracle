import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { ValueBetItem } from '../../models/match.interface';

/** 凱利準則：f* = (p * b - q) / b，其中 b = decimal_odds - 1, p = 勝率, q = 1-p */
@Component({
  selector: 'vb-kelly-calculator',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule
  ],
  templateUrl: './kelly-calculator.component.html',
  styleUrl: './kelly-calculator.component.scss'
})
export class KellyCalculatorComponent {
  @Input() match!: ValueBetItem;
  @Output() closed = new EventEmitter<void>();

  bankroll = 1000;

  get suggestedStake(): number {
    const p = this.match.ai_home_win_prob;
    const q = 1 - p;
    const b = this.match.decimal_odds - 1;
    if (b <= 0) return 0;
    const kelly = (p * b - q) / b;
    const fraction = Math.max(0, Math.min(kelly, 0.25)); // 上限 25% 本金
    return this.bankroll * fraction;
  }

  close(): void {
    this.closed.emit();
  }
}
