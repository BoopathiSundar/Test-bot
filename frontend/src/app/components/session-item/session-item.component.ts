import {
  Component,
  EventEmitter,
  HostListener,
  Input,
  Output,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { firstValueFrom } from 'rxjs';
import { SessionService } from '../../core/session.service';
import { SessionRow } from '../../models/session.model';

@Component({
  selector: 'app-session-item',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './session-item.component.html',
  styleUrls: ['./session-item.component.scss'],
})
export class SessionItemComponent {
  @Input() session!: SessionRow;
  @Input() current = false;
  @Input() archivedView = false;
  @Output() select = new EventEmitter<string>();
  @Output() changed = new EventEmitter<void>();

  menuOpen = false;
  menuLeft = 0;
  menuTop = 0;
  editing = false;
  newName = '';

  constructor(private sessionService: SessionService) {}

  get displayName(): string {
    const raw = this.session.label;
    if (raw) {
      try {
        const parsed = JSON.parse(raw);
        if (
          Array.isArray(parsed) &&
          parsed.length > 0 &&
          parsed[0] &&
          typeof parsed[0].content === 'string'
        ) {
          return String(parsed[0].content);
        }
      } catch {
        /* not JSON - use raw */
      }
    }
    return raw && String(raw).trim() ? String(raw) : 'Untitled';
  }

  @HostListener('document:click', ['$event'])
  onDocumentClick(): void {
    this.menuOpen = false;
  }

  showMenu(event: MouseEvent): void {
    event.stopPropagation();
    this.menuLeft = event.clientX;
    this.menuTop = event.clientY;
    this.menuOpen = true;
  }

  onSelect(): void {
    this.select.emit(this.session.id);
  }

  async togglePin(): Promise<void> {
    this.menuOpen = false;
    try {
      await firstValueFrom(
        this.sessionService.setPinned(this.session.id, !this.session.isPinned)
      );
    } catch {
      /* ignore */
    }
    this.changed.emit();
  }

  async toggleArchive(): Promise<void> {
    this.menuOpen = false;
    try {
      await firstValueFrom(
        this.sessionService.setArchived(this.session.id, !this.session.isArchived)
      );
    } catch {
      /* ignore */
    }
    this.changed.emit();
  }

  startRename(): void {
    this.editing = true;
    this.newName = this.displayName;
    this.menuOpen = false;
    setTimeout(() => {
      const el: HTMLInputElement | null = document.querySelector(
        '.session-rename-input'
      );
      if (el) el.select();
    }, 0);
  }

  async commitRename(): Promise<void> {
    if (!this.editing) return;
    this.editing = false;
    const name = this.newName.trim();
    if (name && name !== this.displayName) {
      try {
        await firstValueFrom(this.sessionService.rename(this.session.id, name));
      } catch {
        /* ignore */
      }
    }
    this.changed.emit();
  }

  cancelRename(): void {
    this.editing = false;
  }

  async delete(): Promise<void> {
    if (!confirm('Delete this chat?')) return;
    this.menuOpen = false;
    try {
      await firstValueFrom(this.sessionService.delete(this.session.id));
    } catch {
      /* ignore */
    }
    this.changed.emit();
  }
}