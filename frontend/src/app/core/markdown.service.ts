import { Injectable } from '@angular/core';
import { marked } from 'marked';
import hljs from 'highlight.js/lib/common';

/**
 * Markdown rendering + code highlighting + copy-code buttons.
 * Same libraries (marked, highlight.js) the old frontend used via CDN.
 */
@Injectable({ providedIn: 'root' })
export class MarkdownService {
  render(text: string): string {
    try {
      return marked.parse(text || '') as string;
    } catch {
      return text || '';
    }
  }

  highlight(root: HTMLElement): void {
    root.querySelectorAll('pre code').forEach((block) => {
      try {
        hljs.highlightElement(block as HTMLElement);
      } catch {
        /* ignore highlight failures */
      }
    });
  }

  attachCopyButtons(root: HTMLElement): void {
    root.querySelectorAll('pre').forEach((pre) => {
      const code = pre.querySelector('code');
      if (!code) return;
      // Avoid duplicate buttons on re-render.
      if (pre.querySelector('.copy-code-btn')) return;

      const btn = document.createElement('button');
      btn.className = 'copy-code-btn';
      btn.type = 'button';
      btn.innerText = 'Copy code';

      btn.addEventListener('click', async () => {
        try {
          await navigator.clipboard.writeText(code.textContent?.trim() ?? '');
          btn.innerText = 'Copied!';
          btn.classList.add('copied');
          setTimeout(() => {
            btn.innerText = 'Copy code';
            btn.classList.remove('copied');
          }, 2000);
        } catch {
          btn.innerText = 'Copy failed';
        }
      });

      pre.appendChild(btn);
    });
  }
}