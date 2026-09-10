import {
  Component,
  EventEmitter,
  HostListener,
  Input,
  OnInit,
  Output,
  ChangeDetectorRef,
  inject
} from '@angular/core';

import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import {
  Session,
  SessionChat,
  SessionService
} from '../../services/session.service';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule
  ],
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.css']
})
export class SidebarComponent implements OnInit {

  // ============================================================
  // SESSION DATA
  // ============================================================

  sessions: Session[] = [];

  // Loading session list
  loading = false;

  // Loading messages for selected session
  loadingChat = false;

  chatError: string | null = null;


  // ============================================================
  // CURRENT SESSION
  // ============================================================

  @Input() currentSessionId: string | null = null;


  // ============================================================
  // EVENTS
  // ============================================================

  // When user selects an existing chat
  @Output() sessionSelected =
    new EventEmitter<string>();

  // When user clicks New Chat
  @Output() newChat =
    new EventEmitter<void>();

  // When saved chat messages are loaded
  @Output() chatLoaded =
    new EventEmitter<{
      id: string;
      messages: SessionChat[];
    }>();


  // ============================================================
  // CONTEXT MENU
  // ============================================================

  menuVisible = false;

  menuLeft = 0;

  menuTop = 0;

  menuSessionId: string | null = null;


  // ============================================================
  // RENAME
  // ============================================================

  renamingId: string | null = null;

  renameValue = '';


  // ============================================================
  // SERVICES
  // ============================================================

  private cdr = inject(ChangeDetectorRef);

  constructor(
    private sessionService: SessionService
  ) {}


  // ============================================================
  // INITIALIZATION
  // ============================================================

  ngOnInit(): void {

    console.log('SIDEBAR INITIALIZED');

    this.loadSessions();
  }


  // ============================================================
  // LOAD ALL SESSIONS
  // ============================================================

  loadSessions(): void {

    console.log(
      '========== LOAD SESSIONS START =========='
    );

    this.loading = true;

    this.sessionService
      .getSessions()
      .subscribe({

        next: (sessions) => {

          console.log(
            'Sessions API response:',
            sessions
          );

          console.log(
            'Is Array:',
            Array.isArray(sessions)
          );

          console.log(
            'Session count:',
            sessions?.length
          );

          /*
           * SessionService already converts the
           * backend response into Session objects.
           *
           * Do NOT map the rows again here.
           */
          this.sessions = sessions || [];

          console.log(
            'Final sessions:',
            this.sessions
          );

          console.log(
            'Final session count:',
            this.sessions.length
          );

          this.loading = false;

          console.log(
            'loading =',
            this.loading
          );

          /*
           * Ensure the Angular view is updated
           * after the HTTP response.
           */
          this.cdr.detectChanges();

        },

        error: (error) => {

          console.error(
            'Failed to load sessions:',
            error
          );

          this.sessions = [];

          this.loading = false;

          this.cdr.detectChanges();
        }

      });
  }


  // ============================================================
  // DISPLAY SESSION NAME
  // ============================================================

  displayName(
    session: Session
  ): string {

    const label =
      session.label;

    if (!label) {
      return 'Untitled chat';
    }

    /*
     * Backend may return the label as:
     *
     * [{"role":"user","content":"Hello"}]
     *
     * Convert that JSON into:
     *
     * Hello
     */

    try {

      const parsed =
        JSON.parse(label);

      if (
        Array.isArray(parsed) &&
        parsed.length > 0 &&
        parsed[0] &&
        typeof parsed[0].content === 'string'
      ) {

        const content =
          String(parsed[0].content);

        if (content.trim()) {
          return content;
        }
      }

    } catch {
      /*
       * Label is already normal text.
       */
    }

    const trimmed =
      String(label).trim();

    if (trimmed) {
      return trimmed;
    }

    return 'Untitled chat';
  }


  // ============================================================
  // SELECT SESSION
  // ============================================================

  selectSession(
    sessionId: string
  ): void {

    console.log(
      'Selected session:',
      sessionId
    );

    /*
     * Tell parent which session is selected.
     */
    this.sessionSelected.emit(
      sessionId
    );

    /*
     * Load messages for the selected session.
     */
    this.loadChat(sessionId);
  }


  // ============================================================
  // LOAD CHAT MESSAGES
  // ============================================================

  private loadChat(
    sessionId: string
  ): void {

    console.log(
      '========== LOAD CHAT START =========='
    );

    console.log(
      'Loading chat:',
      sessionId
    );

    this.loadingChat = true;

    this.chatError = null;

    /*
     * Clear the old loading/error state in the UI.
     */
    this.cdr.detectChanges();

    this.sessionService
      .loadSession(sessionId)
      .subscribe({

        next: (messages) => {

          console.log(
            '========== CHAT API SUCCESS =========='
          );

          console.log(
            'Session ID:',
            sessionId
          );

          console.log(
            'Loaded messages:',
            messages
          );

          console.log(
            'Is Array:',
            Array.isArray(messages)
          );

          console.log(
            'Message count:',
            messages?.length
          );

          /*
           * IMPORTANT:
           * Stop the loading indicator.
           */
          this.loadingChat = false;

          /*
           * Send messages to parent component.
           */
          this.chatLoaded.emit({
            id: sessionId,
            messages: messages || []
          });

          console.log(
            'chatLoaded event emitted'
          );

          console.log(
            'loadingChat =',
            this.loadingChat
          );

          /*
           * Update UI.
           */
          this.cdr.detectChanges();
        },

        error: (error) => {

          console.error(
            '========== CHAT API ERROR =========='
          );

          console.error(
            'Failed to load session messages:',
            error
          );

          this.loadingChat = false;

          this.chatError =
            'Could not load this chat.';

          this.cdr.detectChanges();
        }

      });
  }


  // ============================================================
  // NEW CHAT
  // ============================================================

  onNewChat(): void {

    console.log(
      'NEW CHAT CLICKED'
    );

    /*
     * Do NOT clear this.sessions.
     *
     * Existing chats should remain visible
     * in the sidebar.
     */

    this.loadingChat = false;

    this.chatError = null;

    /*
     * Tell parent to clear the main chat area.
     */
    this.newChat.emit();

    this.cdr.detectChanges();
  }


  // ============================================================
  // REFRESH SESSIONS
  // ============================================================

  refreshSessions(): void {

    console.log(
      'Refreshing sessions...'
    );

    this.loading = true;

    this.sessionService
      .getSessions()
      .subscribe({

        next: (sessions) => {

          console.log(
            'Sessions from SessionService:',
            sessions
          );

          this.sessions =
            sessions || [];

          this.loading = false;

          console.log(
            'Refreshed session count:',
            this.sessions.length
          );

          this.cdr.detectChanges();
        },

        error: (error) => {

          console.error(
            'Failed to refresh sessions:',
            error
          );

          this.loading = false;

          this.cdr.detectChanges();
        }

      });
  }


  // ============================================================
  // CONTEXT MENU
  // ============================================================

  openMenu(
    event: MouseEvent,
    sessionId: string
  ): void {

    event.stopPropagation();

    this.menuSessionId =
      sessionId;

    this.menuLeft =
      event.clientX;

    this.menuTop =
      event.clientY;

    this.menuVisible = true;
  }


  @HostListener(
    'document:click'
  )
  onDocumentClick(): void {

    this.closeMenu();
  }


  closeMenu(): void {

    this.menuVisible = false;

    this.menuSessionId = null;
  }


  // ============================================================
  // FIND SESSION
  // ============================================================

  getSessionById(
    id: string | null
  ): Session | null {

    if (!id) {
      return null;
    }

    return (
      this.sessions.find(
        session =>
          session.id === id
      ) || null
    );
  }


  // ============================================================
  // RENAME
  // ============================================================

  startRename(
    session: Session | null
  ): void {

    if (!session) {
      return;
    }

    this.closeMenu();

    this.renamingId =
      session.id;

    this.renameValue =
      this.displayName(session);

    setTimeout(() => {

      const element =
        document.querySelector<HTMLInputElement>(
          '.sidebar-rename-input'
        );

      if (element) {

        element.focus();

        element.select();
      }

    });
  }


  cancelRename(): void {

    this.renamingId = null;

    this.renameValue = '';
  }


  commitRename(): void {

    const sessionId =
      this.renamingId;

    this.renamingId = null;

    if (!sessionId) {
      return;
    }

    const newName =
      this.renameValue.trim();

    if (!newName) {
      return;
    }

    console.log(
      'Renaming session:',
      sessionId,
      newName
    );

    this.sessionService
      .renameSession(
        sessionId,
        newName
      )
      .subscribe({

        next: () => {

          console.log(
            'Session renamed'
          );

          /*
           * Reload sessions so the
           * new name appears immediately.
           */
          this.refreshSessions();
        },

        error: (error) => {

          console.error(
            'Rename failed:',
            error
          );
        }

      });
  }


  // ============================================================
  // DELETE SESSION
  // ============================================================

  deleteSession(
    sessionId: string
  ): void {

    this.closeMenu();

    const confirmed =
      confirm(
        'Delete this chat?'
      );

    if (!confirmed) {
      return;
    }

    console.log(
      'Deleting session:',
      sessionId
    );

    this.sessionService
      .deleteSession(sessionId)
      .subscribe({

        next: () => {

          console.log(
            'Session deleted'
          );

          /*
           * If the deleted chat was
           * currently selected, start
           * a new chat.
           */
          if (
            sessionId ===
            this.currentSessionId
          ) {

            this.onNewChat();
          }

          /*
           * Reload sidebar.
           */
          this.refreshSessions();
        },

        error: (error) => {

          console.error(
            'Delete failed:',
            error
          );
        }

      });
  }

}