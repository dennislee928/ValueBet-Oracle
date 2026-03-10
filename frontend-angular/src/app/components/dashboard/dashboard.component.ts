import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DataService } from '../../services/data.service';
import { MatchCardComponent } from '../match-card/match-card.component';
import { KellyCalculatorComponent } from '../kelly-calculator/kelly-calculator.component';
import { ValueBetItem } from '../../models/match.interface';
import { MatCardModule } from '@angular/material/card';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { Observable } from 'rxjs';

@Component({
  selector: 'vb-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    MatchCardComponent,
    KellyCalculatorComponent,
    MatCardModule,
    MatProgressSpinnerModule
  ],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss'
})
export class DashboardComponent {
  private data = inject(DataService);
  valueBets$: Observable<ValueBetItem[]> = this.data.getValueBetsPolling(60_000);
  selectedMatch: ValueBetItem | null = null;

  onSelectMatch(m: ValueBetItem): void {
    this.selectedMatch = m;
  }
}

