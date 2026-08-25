import {
  Component,
  EventEmitter,
  HostListener,
  Input,
  OnInit,
  Output,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Session, SessionService } from '../../services/session.service';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.css'],
})
export class SidebarComponent implements OnInit {
  /** Loaded from GET /sessions - never hardcoded. */
  sessions: Session[] = [];
  loading = false;

  /** Id of the currently active session (for highlighting). */
  @Input() currentSessionId: string | null = null;

  /** Emits the backend-provided session_id when a session is clicked. */
  @Output() sessionSelected = new EventEmitter<string>();

  // Context menu state
  menuVisible = false;
  menuLeft = 0;
  menuTop = 0;
  menuSessionId: string | null = null;

  // Inline rename state
  renamingId: string | null = null;
  renameValue = '';

  constructor(private sessionService: SessionService) {}

  ngOnInit(): void {
    this.refreshSessions();
  }

  /** Reload sessions from GET /sessions. */
  refreshSessions(): void {
    this.loading = true;
    this.sessionService.getSessions().subscribe({
      next: (sessions) => {
        this.sessions = sessions;
        this.loading = false;
      },
      error: (err) => {
        console.error('Failed to load sessions:', err);
        this.loading = false;
      },
    });
  }

  /** Decode the display label from the backend (may be JSON-wrapped). */
  displayName(session: Session): string {
    const label = session.label;
    if (label) {
      try {
        const parsed = JSON.parse(label);
        if (
          Array.isArray(parsed) &&
          parsed.length > 0 &&
          parsed[0] &&
          typeof parsed[0].content === 'string'
        ) {
          const content = String(parsed[0].content);
          if (content.trim()) return content;
        }
      } catch {
        /* not JSON - use raw label below */
      }
      const trimmed = String(label).trim();
      if (trimmed) return trimmed;
    }
    return 'Untitled chat';
  }

  /** Handle a session click - emit the backend session_id to the parent. */
  selectSession(sessionId: string): void {
    this.sessionSelected.emit(sessionId);
  }

  // ---------- Context menu ----------

  openMenu(event: MouseEvent, sessionId: string): void {
    event.stopPropagation();
    this.menuSessionId = sessionId;
    this.menuLeft = event.clientX;
    this.menuTop = event.clientY;
    this.menuVisible = true;
  }

  @HostListener('document:click')
  onDocumentClick(): void {
    this.closeMenu();
  }

  /** Look up a session object by id for the context menu actions. */
  getSessionById(id: string | null): Session | null {
    if (!id) return null;
    return this.sessions.find((s) => s.id === id) || null;
  }

  closeMenu(): void {
    this.menuVisible = false;
    this.menuSessionId = null;
  }

  // ---------- Rename ----------

  startRename(session: Session | null): void {
    if (!session) return;
    this.closeMenu();
    this.renamingId = session.id;
    this.renameValue = this.displayName(session);
    // Give the DOM a tick to render the input, then focus + select.
    setTimeout(() => {
      const el = document.querySelector<HTMLInputElement>('.sidebar-rename-input');
      if (el) el.select();
    });
  }

  cancelRename(): void {
    this.renamingId = null;
  }

  commitRename(): void {
    const sessionId = this.renamingId;
    this.renamingId = null;
    if (!sessionId) return;

    const newName = this.renameValue.trim();
    if (!newName) return;

    this.sessionService.renameSession(sessionId, newName).subscribe({
      next: () => this.refreshSessions(),
      error: (err) => console.error('Rename failed:', err),
    });
  }

  // ---------- Delete ----------

  deleteSession(sessionId: string): void {
    this.closeMenu();
    // Confirmation before deleting.
    if (!confirm('Delete this chat?')) return;

    this.sessionService.deleteSession(sessionId).subscribe({
      next: () => this.refreshSessions(),
      error: (err) => console.error('Delete failed:', err),
    });
  }
}