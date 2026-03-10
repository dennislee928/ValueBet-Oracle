import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, interval, switchMap, startWith, shareReplay, of, catchError } from 'rxjs';
import { ValueBetItem } from '../models/match.interface';

/** Rust Gateway 預設位址 */
const GATEWAY_URL = 'http://localhost:3000';

@Injectable({
  providedIn: 'root'
})
export class DataService {
  private readonly apiUrl = `${GATEWAY_URL}/api/value-bets`;

  constructor(private http: HttpClient) {}

  getValueBets(): Observable<ValueBetItem[]> {
    return this.http.get<ValueBetItem[]>(this.apiUrl);
  }

  /** 每 60 秒向 Rust 請求一次最新賠率/價值投注資料的輪詢；失敗時回傳空陣列 */
  getValueBetsPolling(intervalMs: number = 60_000): Observable<ValueBetItem[]> {
    return interval(intervalMs).pipe(
      startWith(0),
      switchMap(() => this.getValueBets().pipe(catchError(() => of([])))),
      shareReplay(1)
    );
  }
}
