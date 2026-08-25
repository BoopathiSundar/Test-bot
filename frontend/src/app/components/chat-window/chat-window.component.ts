import { Component, ElementRef, EventEmitter, Output, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChatService } from '../../core/chat.service';
import { MarkdownDirective } from '../../shared/markdown.directive';
import { ChatMessage, decodeUserMessage } from '../../models/session.model';

@Component({
  selector: 'app-chat-window',
  standalone: true,
  imports: [CommonModule, FormsModule, MarkdownDirective],
  templateUrl: './chat-window.component.html',
  styleUrls: ['./chat-window.component.scss'],
})
export class ChatWindowComponent {
  messages: ChatMessage[] = [];
  input = '';
  busy = false;

  @Output() saved = new EventEmitter<void>();
  @Output() titleChange = new EventEmitter<string>();
  @ViewChild('scroller') scroller?: ElementRef<HTMLElement>;

  constructor(private chatService: ChatService) {}

  async send(): Promise<void> {
    const text = this.input.trim();
    if (!text || this.busy) return;

    this.input = '';
    this.busy = true;
    this.titleChange.emit(text.length > 30 ? text.slice(0, 30) + '…' : text);

    this.messages.push({ role: 'user', content: text });
    const botMsg: ChatMessage = { role: 'assistant', content: '', streaming: true };
    this.messages.push(botMsg);
    this.scrollToBottom();

    try {
      await this.chatService.streamChat(
        [{ role: 'user', content: text }],
        (_token, full) => {
          botMsg.content = full;
          this.scrollToBottom();
        }
      );
      botMsg.streaming = false;
      this.saved.emit();
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      botMsg.content = '[Error: ' + msg + ']';
      botMsg.streaming = false;
    } finally {
      this.busy = false;
      this.scrollToBottom();
    }
  }

  reset(): void {
    this.messages = [];
    this.busy = false;
    this.input = '';
    this.scrollToBottom();
  }

  /** Load a saved session's message pairs from the backend. */
  loadSession(chats: [string, string][]): void {
    this.messages = [];
    chats.forEach((pair) => {
      this.messages.push({ role: 'user', content: decodeUserMessage(pair[0]) });
      this.messages.push({ role: 'assistant', content: pair[1] ?? '' });
    });
    this.busy = false;
    this.input = '';
    this.scrollToBottom();
  }

  private scrollToBottom(): void {
    requestAnimationFrame(() => {
      const el = this.scroller?.nativeElement;
      if (el) el.scrollTop = el.scrollHeight;
    });
  }
}