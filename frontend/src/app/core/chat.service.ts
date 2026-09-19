import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

export interface StreamMessage {
  role: string;
  content: string;
}

/**
 * Talks to the unchanged Flask `/chat-stream` endpoint.
 * Exact same streaming semantics as the original script.js:
 * fetch + ReadableStream reader, decoded token-by-token.
 */
@Injectable({ providedIn: 'root' })
export class ChatService {
  async streamChat(
    messages: StreamMessage[],
    onToken: (token: string, fullText: string) => void,
    sessionId?: string
  ): Promise<string> {
    const payload: { messages: StreamMessage[]; session_id?: string } = {
      messages,
    };
    // Optional per-chat session id so a "new chat" is saved as its own
    // session. When omitted the backend keeps the legacy global behavior.
    if (sessionId) {
      payload.session_id = sessionId;
    }

    const response = await fetch('/chat-stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!response.ok || !response.body) {
      throw new Error('Request failed with status ' + response.status);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let fullText = '';

    for (;;) {
      const { value, done } = await reader.read();
      if (done) break;
      const token = decoder.decode(value, { stream: true });
      fullText += token;
      onToken(token, fullText);
    }

    return fullText;
  }

  constructor(private http: HttpClient) {}
  askRag(question: string, sessionId: string) {
  return this.http.post<any>(
    'http://localhost:5000/ask-rag',
    {
      question: question,
      session_id: sessionId
    }
  );
}
}