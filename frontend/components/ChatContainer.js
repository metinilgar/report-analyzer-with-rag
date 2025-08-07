import { useState, useRef, useEffect } from 'react';
import { FiSend } from 'react-icons/fi';
import { useChat } from '@/contexts/ChatContext';
import ChatMessage from './ChatMessage';

const ChatContainer = () => {
  const { messages, sendMessage, isLoading } = useChat();
  const [inputMessage, setInputMessage] = useState('');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Mesajlar değiştiğinde otomatik scroll
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Textarea başlangıç yüksekliğini ayarla
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = '56px';
    }
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const message = inputMessage;
    setInputMessage('');
    // Textarea yüksekliğini sıfırla
    if (inputRef.current) {
      inputRef.current.style.height = '56px';
    }
    console.log('Mesaj gönderiliyor:', message);
    await sendMessage(message);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  // Textarea otomatik yükseklik ayarlama
  const autoResize = (textarea) => {
    if (textarea) {
      textarea.style.height = 'auto';
      const scrollHeight = textarea.scrollHeight;
      const maxHeight = 200; // maksimum yükseklik
      const minHeight = 56; // minimum yükseklik
      
      textarea.style.height = Math.min(Math.max(scrollHeight, minHeight), maxHeight) + 'px';
    }
  };

  const handleInputChange = (e) => {
    setInputMessage(e.target.value);
    autoResize(e.target);
  };

  // Mesaj yokken ana sayfa görünümü
  if (messages.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full bg-white dark:bg-gray-900 px-4">
        <div className="w-full max-w-4xl">
          {/* Hoş geldin mesajı */}
          <div className="text-center mb-8">
            <h2 className="text-2xl font-semibold text-gray-700 dark:text-gray-300 mb-2">
              Rapor Analiz Asistanına Hoş Geldiniz
            </h2>
            <p className="text-gray-500 dark:text-gray-400">
              Sormak istediğiniz soruları yazarak başlayabilirsiniz.
            </p>
          </div>

          {/* Ortada textarea */}
          <form onSubmit={handleSubmit}>
            <div className="relative flex items-center">
              <textarea
                ref={inputRef}
                value={inputMessage}
                onChange={handleInputChange}
                onKeyDown={handleKeyDown}
                placeholder="Sorunuzu yazın..."
                rows="1"
                className="flex-1 resize-none outline-none border border-gray-300 dark:border-gray-600 
                  rounded-2xl px-4 py-4 pr-12
                  bg-white dark:bg-gray-800 
                  text-gray-900 dark:text-white
                  placeholder-gray-500 dark:placeholder-gray-400
                  focus:border-blue-500 dark:focus:border-blue-400
                  transition-colors overflow-hidden"
                style={{ minHeight: '56px', maxHeight: '200px', height: '56px' }}
              />
              <button
                type="submit"
                disabled={!inputMessage.trim() || isLoading}
                className="absolute right-2 p-2 rounded-lg 
                  bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 dark:disabled:bg-gray-600
                  text-white transition-colors
                  disabled:cursor-not-allowed"
              >
                <FiSend className="w-5 h-5" />
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  }

  // Mesajlar varken normal görünüm (textarea altta)
  return (
    <div className="flex flex-col h-full bg-white dark:bg-gray-900">
      {/* Mesajlar Alanı */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto py-4 px-4">
          <div className="space-y-4">
            {messages.map((message, index) => (
              <ChatMessage key={index} message={message} />
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 dark:bg-gray-800 rounded-lg px-4 py-2">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>
      </div>

      {/* Mesaj Giriş Alanı */}
      <form onSubmit={handleSubmit} className="pb-4 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="relative flex items-center">
            <textarea
              ref={inputRef}
              value={inputMessage}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              placeholder="Sorunuzu yazın..."
              rows="1"
              className="flex-1 resize-none outline-none border border-gray-300 dark:border-gray-600 
                rounded-2xl px-4 py-4 pr-12
                bg-white dark:bg-gray-800 
                text-gray-900 dark:text-white
                placeholder-gray-500 dark:placeholder-gray-400
                focus:border-blue-500 dark:focus:border-blue-400
                transition-colors overflow-hidden"
              style={{ minHeight: '56px', maxHeight: '200px', height: '56px' }}
            />
            <button
              type="submit"
              disabled={!inputMessage.trim() || isLoading}
              className="absolute right-2 p-2 rounded-lg 
                bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 dark:disabled:bg-gray-600
                text-white transition-colors
                disabled:cursor-not-allowed"
            >
              <FiSend className="w-5 h-5" />
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};

export default ChatContainer; 