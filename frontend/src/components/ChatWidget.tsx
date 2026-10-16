import { useState, useEffect, useRef } from 'react';
import { MessageSquare, X, Send, Upload, Minimize2, Maximize2 } from 'lucide-react';
import { chatService, ChatMessage, ChatSession } from '../services/chat';

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen && !sessionId) {
      initializeChat();
    }
  }, [isOpen, sessionId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const initializeChat = async () => {
    try {
      const session = await chatService.createSession('AI Assistant');
      setSessionId(session.id);
      setMessages([
        {
          id: 0,
          session_id: session.id,
          role: 'assistant',
          content: 'Hello! I\'m your AI Business Assistant. You can ask me questions about your sales, customers, products, or upload CSV files for analysis. How can I help you today?',
          metadata: null,
          created_at: new Date().toISOString(),
        },
      ]);
    } catch (error) {
      console.error('Failed to initialize chat:', error);
    }
  };

  const handleSendMessage = async () => {
    if (!message.trim() || !sessionId || loading) return;

    const userMessage = message;
    setMessage('');
    setLoading(true);

    // Add user message
    const userMsg: ChatMessage = {
      id: Date.now(),
      session_id: sessionId,
      role: 'user',
      content: userMessage,
      metadata: null,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);

    try {
      const response = await chatService.sendMessage(sessionId, userMessage);
      setMessages((prev) => [...prev, response]);
    } catch (error) {
      console.error('Failed to send message:', error);
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          session_id: sessionId,
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.',
          metadata: null,
          created_at: new Date().toISOString(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.csv')) {
      alert('Please upload a CSV file');
      return;
    }

    setUploading(true);

    try {
      const result = await chatService.uploadCSV(file);

      const analysisMsg: ChatMessage = {
        id: Date.now(),
        session_id: sessionId || 0,
        role: 'assistant',
        content: `File "${file.name}" uploaded successfully!\n\nAnalysis:\n- Rows: ${result.analysis.rows}\n- Columns: ${result.analysis.columns.join(', ')}\n\nYou can now ask questions about this data.`,
        metadata: result.analysis,
        created_at: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, analysisMsg]);
    } catch (error) {
      console.error('Failed to upload file:', error);
      alert('Failed to upload file. Please try again.');
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 bg-navy-600 hover:bg-navy-700 text-white p-4 rounded-full shadow-lg transition-all duration-200 z-50"
        title="Open AI Assistant"
      >
        <MessageSquare className="w-6 h-6" />
      </button>
    );
  }

  return (
    <div className="fixed bottom-6 right-6 w-96 bg-white rounded-lg shadow-2xl z-50 flex flex-col max-h-[600px]">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-navy-900 text-white rounded-t-lg">
        <div className="flex items-center space-x-2">
          <MessageSquare className="w-5 h-5" />
          <span className="font-semibold">AI Business Assistant</span>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setIsMinimized(!isMinimized)}
            className="p-1 hover:bg-navy-800 rounded transition-colors"
          >
            {isMinimized ? <Maximize2 className="w-4 h-4" /> : <Minimize2 className="w-4 h-4" />}
          </button>
          <button
            onClick={() => setIsOpen(false)}
            className="p-1 hover:bg-navy-800 rounded transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {!isMinimized && (
        <>
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 min-h-[300px] max-h-[400px]">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] p-3 rounded-lg ${
                    msg.role === 'user'
                      ? 'bg-navy-600 text-white'
                      : 'bg-gray-100 text-gray-900'
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 p-3 rounded-lg">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200"></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="p-4 border-t border-gray-200">
            <div className="flex items-center space-x-2 mb-2">
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileUpload}
                accept=".csv"
                className="hidden"
                id="csv-upload"
              />
              <label
                htmlFor="csv-upload"
                className={`flex items-center space-x-1 px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg cursor-pointer transition-colors ${
                  uploading ? 'opacity-50 cursor-not-allowed' : ''
                }`}
              >
                <Upload className="w-4 h-4" />
                <span className="text-sm">{uploading ? 'Uploading...' : 'Upload CSV'}</span>
              </label>
            </div>
            <div className="flex items-center space-x-2">
              <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about your business data..."
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-navy-500"
                disabled={loading}
              />
              <button
                onClick={handleSendMessage}
                disabled={!message.trim() || loading}
                className="p-2 bg-navy-600 hover:bg-navy-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
