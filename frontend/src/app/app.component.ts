import { Component, ViewChild, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { SidebarComponent } from './components/sidebar/sidebar.component';
import { SessionChat } from './services/session.service';
import { ChatService } from './core/chat.service';
import { decodeUserMessage } from './models/session.model';

/** A single new-chat message pair still streaming from the backend. */
interface LivePair {
  user: string;
  bot: string;
  streaming: boolean;
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule, SidebarComponent],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
})
export class AppComponent {
  /** Id of the session currently shown in the main area. */
  selectedSessionId: string | null = null;

  /** Saved message pairs of the selected session. */
  sessionMessages: SessionChat[] = [];

  /** Composer input shared by the new-chat hero and the chat composer. */
  input = '';

  /** True while a new-chat request is streaming. */
  busy = false;

  /** The in-progress new chat (streaming live message pair). */
  livePair: LivePair | null = null;

  private readonly chatService = inject(ChatService);

  @ViewChild(SidebarComponent) sidebar?: SidebarComponent;

  onSessionSelected(sessionId: string): void {
    this.selectedSessionId = sessionId;
    this.resetComposerState();
  }

  onChatLoaded(event: { id: string; messages: SessionChat[] }): void {
    this.selectedSessionId = event.id;
    this.sessionMessages = event.messages;
    this.resetComposerState();
  }

  onNewChat(): void {
    // Clear the chat area and show the ChatGPT-style composer.
    this.selectedSessionId = null;
    this.resetComposerState();
  }

  /** Decode the stored user_message column (may be JSON-wrapped). */
  userText(message: SessionChat): string {
    return decodeUserMessage(message.user);
  }

  onEnterKey(event: Event): void {
    const keyEvent = event as KeyboardEvent;
    if (keyEvent.shiftKey) {
      // Shift+Enter inserts a new line (like ChatGPT).
      return;
    }
    keyEvent.preventDefault();
    void this.send();
  }

  /** Submit the composer. The first message creates + saves a session. */
  async send(): Promise<void> {
    const text = this.input.trim();
    if (!text || this.busy) return;

    // A brand new chat gets a fresh session id. It is saved server-side
    // under this id and then shows up in the sidebar session list.
    if (!this.selectedSessionId) {
      this.selectedSessionId = crypto.randomUUID();
    }
    const sessionId = this.selectedSessionId;

    this.input = '';
    this.busy = true;

    const pair: LivePair = { user: text, bot: '', streaming: true };
    this.livePair = pair;

    try {
      const full = await this.chatService.streamChat(
        [{ role: 'user', content: text }],
        (_token, fullText) => {
          pair.bot = fullText;
        },
        sessionId
      );
      pair.bot = full;
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      pair.bot = '[Error: ' + msg + ']';
    } finally {
      pair.streaming = false;
      // Append to history (keeps previously loaded messages intact).
      this.sessionMessages = [
        ...this.sessionMessages,
        { user: pair.user, bot: pair.bot },
      ];
      this.livePair = null;
      this.busy = false;
      // Refresh the sidebar so the new chat appears as a saved session.
      this.sidebar?.refreshSessions();
    }
  }

  private resetComposerState(): void {
    this.busy = false;
    this.livePair = null;
    this.input = '';
  }
}