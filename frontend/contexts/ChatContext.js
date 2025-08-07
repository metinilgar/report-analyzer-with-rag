import { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const ChatContext = createContext();

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};

export const ChatProvider = ({ children }) => {
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [conversations, setConversations] = useState([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [pdfViewerOpen, setPdfViewerOpen] = useState(false);
  const [pdfUrl, setPdfUrl] = useState('');
  const [pdfFileName, setPdfFileName] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

  // Konuşmaları yükle
  const loadConversations = async () => {
    try {
      const response = await axios.get(`${backendUrl}/api/conversations/`);
      setConversations(response.data);
    } catch (error) {
      console.error('Konuşmalar yüklenemedi:', error);
      setConversations([]);
    }
  };

  // Mesajın ilk birkaç kelimesini başlık olarak al
  const generateTitleFromMessage = (message) => {
    const words = message.trim().split(' ');
    const firstWords = words.slice(0, 5).join(' '); // İlk 5 kelime
    return firstWords.length > 50 ? firstWords.substring(0, 50) + '...' : firstWords;
  };

  // Yeni konuşma başlat (UI temizle, konuşma oluşturma)
  const startNewChat = () => {
    setCurrentConversationId(null);
    setMessages([]);
    closePdfViewer();
  };

  // Yeni konuşma oluştur
  const createNewConversation = async (title = null) => {
    try {
      const response = await axios.post(`${backendUrl}/api/conversations/new`, {
        title: title,
        user_id: null
      });
      const newConversation = response.data;
      setCurrentConversationId(newConversation.id);
      closePdfViewer(); // Yeni konuşma başladığında PDF viewer'ı kapat
      await loadConversations();
      return newConversation;
    } catch (error) {
      console.error('Yeni konuşma oluşturulamadı:', error);
      return null;
    }
  };

  // Konuşmayı yükle
  const loadConversation = async (conversationId) => {
    try {
      // Konuşma mesajlarını yükle
      const messagesResponse = await axios.get(`${backendUrl}/api/conversations/${conversationId}/messages`);
      
      // MessageResponse'dan ChatMessage formatına dönüştür
      const formattedMessages = messagesResponse.data.map(message => ({
        role: message.sender === 'user' ? 'user' : 'assistant',
        content: message.content,
        id: message.id,
        timestamp: message.timestamp,
        sources: message.sources
      }));
      
      setCurrentConversationId(conversationId);
      setMessages(formattedMessages);
      closePdfViewer(); // Konuşma değiştiğinde PDF viewer'ı kapat
    } catch (error) {
      console.error('Konuşma yüklenemedi:', error);
      setMessages([]);
    }
  };

  // Mesaj gönder
  const sendMessage = async (message) => {
    let conversationId = currentConversationId;
    
    // Eğer aktif konuşma yoksa, yeni konuşma oluştur
    if (!conversationId) {
      const title = generateTitleFromMessage(message);
      const newConv = await createNewConversation(title);
      if (!newConv) {
        setIsLoading(false);
        return;
      }
      conversationId = newConv.id;
    }

    const userMessage = { role: 'user', content: message };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await axios.post(`${backendUrl}/api/chat/`, {
        conversation_id: conversationId,
        message: message
      });

      const assistantMessage = { 
        role: 'assistant', 
        content: response.data.ai_message,
        id: response.data.ai_message_id,
        sources: response.data.sources
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Mesaj gönderilemedi:', error);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin.' 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  // Konuşma başlığını güncelle
  const updateConversationTitle = async (conversationId, newTitle) => {
    try {
      await axios.patch(`${backendUrl}/api/conversations/${conversationId}/title?title=${encodeURIComponent(newTitle)}`);
      
      // Konuşma listesini yenile
      await loadConversations();
      return true;
    } catch (error) {
      console.error('Konuşma başlığı güncellenemedi:', error);
      return false;
    }
  };

  // Konuşmayı sil
  const deleteConversation = async (conversationId) => {
    try {
      await axios.delete(`${backendUrl}/api/conversations/${conversationId}`);
      
      // Eğer silinen konuşma şu anki konuşma ise, temizle
      if (currentConversationId === conversationId) {
        setCurrentConversationId(null);
        setMessages([]);
      }
      
      // Konuşma listesini yenile
      await loadConversations();
      return true;
    } catch (error) {
      console.error('Konuşma silinemedi:', error);
      return false;
    }
  };

  // PDF Viewer'ı aç
  const openPdfViewer = ({ url, fileName }) => {
    setPdfUrl(url);
    setPdfFileName(fileName);
    setPdfViewerOpen(true);
    setSidebarOpen(false); // Sidebar'ı otomatik kapat
  };

  // PDF Viewer'ı kapat
  const closePdfViewer = () => {
    setPdfViewerOpen(false);
    setPdfUrl('');
    setPdfFileName('');
    setSidebarOpen(true); // İsteğe bağlı: Sidebar'ı tekrar aç
  };

  // Component mount olduğunda konuşmaları yükle
  useEffect(() => {
    console.log('Backend URL:', backendUrl);
    loadConversations();
  }, [backendUrl]);

  const value = {
    currentConversationId,
    messages,
    conversations,
    sidebarOpen,
    setSidebarOpen,
    pdfViewerOpen,
    pdfUrl,
    pdfFileName,
    isLoading,
    sendMessage,
    openPdfViewer,
    closePdfViewer,
    startNewChat,
    createNewConversation,
    loadConversation,
    loadConversations,
    updateConversationTitle,
    deleteConversation
  };

  return (
    <ChatContext.Provider value={value}>
      {children}
    </ChatContext.Provider>
  );
}; 