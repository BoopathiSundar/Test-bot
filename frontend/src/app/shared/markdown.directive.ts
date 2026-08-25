import {
  Directive,
  ElementRef,
  Input,
  OnChanges,
  Renderer2,
} from '@angular/core';
import { DomSanitizer, SecurityContext } from '@angular/platform-browser';
import { MarkdownService } from '../core/markdown.service';

/**
 * Renders markdown text into its element, applies syntax highlighting,
 * and attaches copy-code buttons. Re-renders whenever the bound text
 * changes (used to stream live token updates).
 */
@Directive({ selector: '[appMarkdown]', standalone: true })
export class MarkdownDirective implements OnChanges {
  @Input('appMarkdown') text = '';

  constructor(
    private el: ElementRef,
    private renderer: Renderer2,
    private md: MarkdownService,
    private sanitizer: DomSanitizer
  ) {}

  ngOnChanges(): void {
    const html = this.md.render(this.text ?? '');
    const safe = this.sanitizer.sanitize(SecurityContext.HTML, html) ?? '';
    this.renderer.setProperty(this.el.nativeElement, 'innerHTML', safe);
    this.md.highlight(this.el.nativeElement);
    this.md.attachCopyButtons(this.el.nativeElement);
  }
}