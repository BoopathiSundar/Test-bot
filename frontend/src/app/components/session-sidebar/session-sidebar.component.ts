import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SessionService } from '../../core/session.service';
import { SessionRow } from '../../models/session.model';
import { SessionItemComponent } from '../session-item/session-item.component';

@Component({
  selector: 'app-session-sidebar',
  standalone: true,
  imports: [CommonModule, SessionItemComponent],
  templateUrl: './session-sidebar.component.html',
  styleUrls: ['./session-sidebar.component.scss'],
})
export class SessionSidebarComponent implements OnInit {
  sessions: SessionRow[] = [];
  archivedView = false;

  @Input() open = false;
  @Input() currentSessionId: string | null = null;
  @Output() select = new EventEmitter<string>();
  @Output() newChat = new EventEmitter<void>();
  @Output() closeSidebar = new EventEmitter<void>();

  constructor(private sessionService: SessionService) {}

  ngOnInit(): void {
    this.reload();
  }

  reload(): void {
    const request = this.archivedView
      ? this.sessionService.listArchived()
      : this.sessionService.listActive();
    request.subscribe({
      next: (s) => (this.sessions = s),
      error: (err) => console.error('session list error:', err),
    });
  }

  toggleArchived(): void {
    this.archivedView = !this.archivedView;
    this.reload();
  }

  onSelect(sessionId: string): void {
    this.select.emit(sessionId);
    this.closeSidebar.emit();
  }

  onNewChat(): void {
    this.newChat.emit();
    this.closeSidebar.emit();
  }

  onClearAll(): void {
    if (!confirm('Delete all chats?')) return;
    this.sessionService.clearAll().subscribe({
      next: () => {
        this.newChat.emit();
        this.reload();
      },
      error: (err) => console.error('clear error:', err),
    });
  }
}