export interface SessionRow {
  id: string;
  /** Raw label from the backend (may be a JSON-wrapped message array). */
  label: string;
  lastChat: string;
  isPinned: boolean;
  isArchived: boolean;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  streaming?: boolean;
}

/** Helper: decode a stored user_message column (may be JSON-wrapped). */
export function decodeUserMessage(raw: string): string {
  if (!raw) return '';
  try {
    const parsed = JSON.parse(raw);
    if (
      Array.isArray(parsed) &&
      parsed.length > 0 &&
      parsed[0] &&
      typeof parsed[0].content === 'string'
    ) {
      return parsed[0].content;
    }
  } catch {
    /* not JSON - use raw text */
  }
  return raw;
}