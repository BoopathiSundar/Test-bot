import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SidebarComponent } from './components/sidebar/sidebar.component';
import { SessionChat } from './services/session.service';
import { decodeUserMessage } from './models/session.model';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, SidebarComponent],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
})
export class AppComponent {
  /** Id of the session currently shown in the main area. */
  selectedSessionId: string | null = null;

  /** Saved message pairs of the selected session. */
  sessionMessages: SessionChat[] = [];

  onSessionSelected(sessionId: string): void {
    this.selectedSessionId = sessionId;
  }

  onChatLoaded(event: { id: string; messages: SessionChat[] }): void {
    this.selectedSessionId = event.id;
    this.sessionMessages = event.messages;
  }

  onNewChat(): void {
    this.selectedSessionId = null;
    this.sessionMessages = [];
  }

  /** Decode the stored user_message column (may be JSON-wrapped). */
  userText(message: SessionChat): string {
    return decodeUserMessage(message.user);
  }
}