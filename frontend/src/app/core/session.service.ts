import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { SessionRow } from '../models/session.model';

interface ActionResult {
  success: boolean;
}

/** Maps the backend's positional array rows into typed objects. */
function toSessionRow(row: unknown[]): SessionRow {
  return {
    id: String(row[0] ?? ''),
    label: row[1] ? String(row[1]) : '',
    lastChat: row[2] ? String(row[2]) : '',
    isPinned: String(row[3]) === '1',
    isArchived: String(row[4]) === '1',
  };
}

type SessionRowArray = [string, unknown, string, number, number];

/**
 * All session operations against the unchanged Flask API.
 */
@Injectable({ providedIn: 'root' })
export class SessionService {
  constructor(private http: HttpClient) {}

  listActive(): Observable<SessionRow[]> {
    return this.http
      .get<SessionRowArray[]>('/sessions')
      .pipe(map((rows) => rows.map(toSessionRow)));
  }

  listArchived(): Observable<SessionRow[]> {
    return this.http
      .get<SessionRowArray[]>('/archived-chats')
      .pipe(map((rows) => rows.map(toSessionRow)));
  }

  loadChat(sessionId: string): Observable<[string, string][]> {
    return this.http.get<[string, string][]>(`/session/${sessionId}`);
  }

  rename(sessionId: string, name: string): Observable<ActionResult> {
    return this.http.put<ActionResult>(`/rename_session/${sessionId}`, { name });
  }

  delete(sessionId: string): Observable<ActionResult> {
    return this.http.delete<ActionResult>(`/delete_session/${sessionId}`);
  }

  clearAll(): Observable<ActionResult> {
    return this.http.delete<ActionResult>('/clear-chat');
  }

  setPinned(sessionId: string, pinned: boolean): Observable<ActionResult> {
    const url = pinned
      ? `/pin_chat/${sessionId}`
      : `/unpin_chat/${sessionId}`;
    return this.http.post<ActionResult>(url, {});
  }

  setArchived(sessionId: string, archived: boolean): Observable<ActionResult> {
    const url = archived
      ? `/archive_chat/${sessionId}`
      : `/unarchive_chat/${sessionId}`;
    return this.http.post<ActionResult>(url, {});
  }
}