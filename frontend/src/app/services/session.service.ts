import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

/**
 * A single session row as returned by the Flask backend.
 * The backend returns flat arrays, so the raw response is mapped into
 * this typed object by {@link toSession}.
 */
export interface Session {
  /** session_id from the backend - never generated on the client. */
  id: string;
  /** Raw display label from the backend (may be a JSON-wrapped message). */
  label: string;
  /** Last active timestamp (string) from the backend. */
  lastChat: string;
  isPinned: boolean;
  isArchived: boolean;
}

/** Raw item shape returned by GET /sessions (positional array). */
type SessionRowArray = [
  string,        // 0: session_id
  string,        // 1: display label (may be JSON-wrapped)
  string,        // 2: last_chat
  number,        // 3: is_pinned
  number         // 4: is_archived
];

function toSession(row: SessionRowArray): Session {
  return {
    id: String(row[0] ?? ''),
    label: row[1] ? String(row[1]) : '',
    lastChat: row[2] ? String(row[2]) : '',
    isPinned: String(row[3]) === '1',
    isArchived: String(row[4]) === '1',
  };
}

export interface ActionResult {
  success: boolean;
}

/**
 * HTTP service for session operations against the unchanged Flask API.
 * Uses the same endpoints /sessions, /rename_session/<id>, /delete_session/<id>.
 */
@Injectable({ providedIn: 'root' })
export class SessionService {
  constructor(private http: HttpClient) {}

  /** Fetch the active (non-archived) sessions from GET /sessions. */
  getSessions(): Observable<Session[]> {
    return this.http
      .get<SessionRowArray[]>('/sessions')
      .pipe(map((rows) => (rows || []).map(toSession)));
  }

  /** Rename a session via PUT /rename_session/<id> with body { name }. */
  renameSession(id: string, name: string): Observable<ActionResult> {
    return this.http.put<ActionResult>(`/rename_session/${id}`, { name });
  }

  /** Delete a session via DELETE /delete_session/<id>. */
  deleteSession(id: string): Observable<ActionResult> {
    return this.http.delete<ActionResult>(`/delete_session/${id}`);
  }
}