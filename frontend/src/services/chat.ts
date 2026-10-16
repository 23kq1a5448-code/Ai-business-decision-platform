import api from './api';

export interface ChatSession {
  id: number;
  business_id: number;
  user_id: number;
  session_name: string | null;
  created_at: string;
  updated_at: string | null;
}

export interface ChatMessage {
  id: number;
  session_id: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  message_metadata: Record<string, any> | null;
  created_at: string;
}

export const chatService = {
  async createSession(sessionName?: string): Promise<ChatSession> {
    const response = await api.post<ChatSession>('/chat/sessions/', { session_name });
    return response.data;
  },

  async getSessions(): Promise<ChatSession[]> {
    const response = await api.get<ChatSession[]>('/chat/sessions/');
    return response.data;
  },

  async getSession(sessionId: number): Promise<ChatSession> {
    const response = await api.get<ChatSession>(`/chat/sessions/${sessionId}`);
    return response.data;
  },

  async getMessages(sessionId: number): Promise<ChatMessage[]> {
    const response = await api.get<ChatMessage[]>(`/chat/sessions/${sessionId}/messages`);
    return response.data;
  },

  async sendMessage(sessionId: number, content: string): Promise<ChatMessage> {
    const response = await api.post<ChatMessage>(`/chat/sessions/${sessionId}/messages`, {
      role: 'user',
      content,
    });
    return response.data;
  },

  async uploadCSV(file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/chat/upload-csv', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  },
};
