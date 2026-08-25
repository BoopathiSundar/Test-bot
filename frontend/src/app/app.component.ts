import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SidebarComponent } from './components/sidebar/sidebar.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, SidebarComponent],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
})
export class AppComponent {
  /** Holds the backend-provided session id emitted by the sidebar. */
  selectedSessionId: string | null = null;

  onSessionSelected(sessionId: string): void {
    this.selectedSessionId = sessionId;
    // Chat window migration is out of scope - store the id for later use.
  }
}