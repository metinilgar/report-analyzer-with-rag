import { useState, useRef, useEffect } from 'react';
import { FiPlus, FiUpload, FiMessageSquare, FiTrash2, FiMoreVertical, FiEdit3, FiSun, FiMoon, FiMenu, FiSettings, FiFile, FiX, FiDownload, FiEye, FiCalendar, FiHardDrive, FiFileText } from 'react-icons/fi';
import { useChat } from '@/contexts/ChatContext';
import { useTheme } from '@/contexts/ThemeContext';
import DocumentUploadModal from './DocumentUploadModal';
import SettingsModal from './SettingsModal';
import axios from 'axios';

const Sidebar = () => {
  const {
    conversations,
    currentConversationId,
    sidebarOpen,
    setSidebarOpen,
    startNewChat,
    loadConversation,
    updateConversationTitle,
    deleteConversation
  } = useChat();
  
  const { darkMode, toggleDarkMode } = useTheme();
  
  // Hover ve Pin state'leri
  const [isHovered, setIsHovered] = useState(false);
  const [isPinned, setIsPinned] = useState(false);
  
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [conversationToDelete, setConversationToDelete] = useState(null);
  const [renameModalOpen, setRenameModalOpen] = useState(false);
  const [conversationToRename, setConversationToRename] = useState(null);
  const [newTitle, setNewTitle] = useState('');
  const [openDropdownId, setOpenDropdownId] = useState(null);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [documentsModalOpen, setDocumentsModalOpen] = useState(false);
  const [documents, setDocuments] = useState([]);
  const [documentsLoading, setDocumentsLoading] = useState(false);
  const dropdownRef = useRef(null);

  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

  // Sidebar'ın açık olup olmadığını belirle (pin durumu veya hover durumu)
  const isExpanded = isPinned || isHovered;

  // Dropdown dışında tıklama kontrolü
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setOpenDropdownId(null);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleDropdownToggle = (conversationId, e) => {
    e.stopPropagation();
    setOpenDropdownId(openDropdownId === conversationId ? null : conversationId);
  };

  const handleRenameClick = (conversation, e) => {
    e.stopPropagation();
    setConversationToRename(conversation);
    setNewTitle(conversation.title || '');
    setRenameModalOpen(true);
    setOpenDropdownId(null);
  };

  const handleDeleteClick = (conversation, e) => {
    e.stopPropagation();
    setConversationToDelete(conversation);
    setDeleteConfirmOpen(true);
    setOpenDropdownId(null);
  };

  const confirmRename = async () => {
    if (conversationToRename && newTitle.trim()) {
      const success = await updateConversationTitle(conversationToRename.id, newTitle.trim());
      if (success) {
        setRenameModalOpen(false);
        setConversationToRename(null);
        setNewTitle('');
      }
    }
  };

  const cancelRename = () => {
    setRenameModalOpen(false);
    setConversationToRename(null);
    setNewTitle('');
  };

  const confirmDelete = async () => {
    if (conversationToDelete) {
      const success = await deleteConversation(conversationToDelete.id);
      if (success) {
        setDeleteConfirmOpen(false);
        setConversationToDelete(null);
      }
    }
  };

  const cancelDelete = () => {
    setDeleteConfirmOpen(false);
    setConversationToDelete(null);
  };

  // Hover event handlers
  const handleMouseEnter = () => {
    if (!isPinned) {
      setIsHovered(true);
    }
  };

  const handleMouseLeave = () => {
    if (!isPinned) {
      setIsHovered(false);
    }
  };

  // Pin toggle handler
  const togglePin = () => {
    setIsPinned(!isPinned);
    if (!isPinned) {
      // Pin edilince hover durumunu temizle
      setIsHovered(false);
    }
  };

  const fetchDocuments = async () => {
    setDocumentsLoading(true);
    try {
      const response = await axios.get(`${backendUrl}/api/documents/list`);
      console.log('Doküman API yanıtı:', response.data); // Debug için
      console.log('Dokümanlar:', response.data.documents); // Doküman detayları
      
      if (response.data.documents && response.data.documents.length > 0) {
        console.log('İlk doküman örneği:', response.data.documents[0]); // İlk dokümanın tüm özellikleri
      }
      
      setDocuments(response.data.documents || []);
    } catch (error) {
      console.error('Dokümanlar yüklenemedi:', error);
      setDocuments([]);
    } finally {
      setDocumentsLoading(false);
    }
  };

  const openDocumentsModal = () => {
    setDocumentsModalOpen(true);
    fetchDocuments();
  };

  return (
    <>
      <aside
        className={`
          fixed top-0 left-0 h-screen
          ${isExpanded ? 'w-64' : 'w-12'}
          bg-white dark:bg-gray-800 
          border-r border-gray-200 dark:border-gray-700
          transition-all duration-300
          z-30
        `}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
      >
        <div className="flex flex-col h-full">
          {/* Header - Pin Toggle ve RAG */}
          <div className={`${isExpanded ? 'p-4 flex items-center' : 'p-2'}`}>
            {/* Menu/Pin Button - Sol taraf */}
            <button
              onClick={togglePin}
              className={`${isExpanded ? 'p-2 mr-4' : 'w-8 h-8 flex items-center justify-center'} rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors ${isPinned ? 'bg-blue-100 dark:bg-blue-900' : ''}`}
              title={isPinned ? "Sabitlemeyi Kaldır" : "Sidebar'ı Sabitlemek"}
            >
              <FiMenu className={`w-5 h-5 ${isPinned ? 'text-blue-600 dark:text-blue-400' : 'text-gray-600 dark:text-gray-300'}`} />
            </button>
            
            {/* RAG - Ortada */}
            {isExpanded && (
              <h1 className="text-xl font-bold text-gray-800 dark:text-white flex-1 text-center overflow-hidden">
                RAG
              </h1>
            )}
          </div>

          {/* Eylem Butonları */}
          <div className={`${isExpanded ? 'p-4' : 'p-2'} space-y-2`}>
            <button
              onClick={currentConversationId ? startNewChat : undefined}
              disabled={!currentConversationId}
              className={`w-full flex items-center transition-colors h-10
                ${isExpanded 
                  ? `justify-center space-x-2 px-4 rounded-lg ${
                      !currentConversationId 
                        ? 'text-blue-600 dark:text-blue-400 cursor-not-allowed' 
                        : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300'
                    }` 
                  : `w-8 justify-center rounded-lg ${
                      !currentConversationId 
                        ? 'text-blue-600 dark:text-blue-400' 
                        : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-300'
                    }`
                }`}
              title={!currentConversationId ? "Zaten Yeni Sohbet Sayfasındasınız" : "Yeni Sohbet"}
            >
              <FiPlus className={`w-5 h-5 flex-shrink-0 ${!currentConversationId ? 'fill-current' : ''}`} />
              {isExpanded && <span className="truncate min-w-0">Yeni Sohbet</span>}
            </button>
            
            <button
              onClick={() => setUploadModalOpen(true)}
              className={`w-full flex items-center transition-colors h-10
                ${isExpanded 
                  ? 'justify-center space-x-2 hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 px-4 rounded-lg' 
                  : 'w-8 justify-center rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-300'
                }`}
              title="Doküman Yükle"
            >
              <FiUpload className="w-5 h-5 flex-shrink-0" />
              {isExpanded && <span className="truncate min-w-0">Doküman Yükle</span>}
            </button>
          </div>

          {/* Konuşma Listesi - Sadece Açık Modda */}
          {isExpanded && (
            <div className="flex-1 overflow-y-auto px-4">
              <h3 className="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2">
                Konuşmalar
              </h3>
              <div className="space-y-1">
                {conversations.map((conversation) => (
                  <div
                    key={conversation.id}
                    className={`
                      w-full px-3 py-2 rounded-lg
                      flex items-center justify-between
                      transition-colors group relative
                      ${
                        currentConversationId === conversation.id
                          ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-200'
                          : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-200'
                      }
                    `}
                  >
                    <button
                      onClick={() => loadConversation(conversation.id)}
                      className="flex items-center space-x-2 flex-1 min-w-0 text-left"
                    >
                      <FiMessageSquare className="w-4 h-4 flex-shrink-0" />
                      <span className="truncate text-sm min-w-0">
                        {conversation.title || `Konuşma ${conversation.id.slice(0, 8)}...`}
                      </span>
                    </button>
                    
                    <div className="relative" ref={openDropdownId === conversation.id ? dropdownRef : null}>
                      <button
                        onClick={(e) => handleDropdownToggle(conversation.id, e)}
                        className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-600 transition-all flex-shrink-0 ml-2"
                        title="Seçenekler"
                      >
                        <FiMoreVertical className="w-4 h-4" />
                      </button>
                      
                      {openDropdownId === conversation.id && (
                        <div className="absolute right-0 top-8 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg shadow-lg py-1 z-50 min-w-[140px]">
                          <button
                            onClick={(e) => handleRenameClick(conversation, e)}
                            className="w-full px-3 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center space-x-2"
                          >
                            <FiEdit3 className="w-4 h-4" />
                            <span>Yeniden Adlandır</span>
                          </button>
                          <button
                            onClick={(e) => handleDeleteClick(conversation, e)}
                            className="w-full px-3 py-2 text-left text-sm hover:bg-red-50 dark:hover:bg-red-900/20 text-red-600 dark:text-red-400 flex items-center space-x-2"
                          >
                            <FiTrash2 className="w-4 h-4" />
                            <span>Sil</span>
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Ayarlar ve Dokümanlar Butonları */}
          <div className={`${isExpanded ? 'p-4' : 'p-2'} mt-auto space-y-2`}>
            <button
              onClick={openDocumentsModal}
              className={`${isExpanded 
                ? 'w-full flex items-center justify-center space-x-2 h-10 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-300' 
                : 'w-8 h-8 flex items-center justify-center rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-300'
              } transition-all duration-300`}
              title="Dokümanlar"
            >
              <FiFile className="w-5 h-5 flex-shrink-0" />
              {isExpanded && <span className="text-sm truncate min-w-0">Dokümanlar</span>}
            </button>
            
            <button
              onClick={() => setSettingsOpen(true)}
              className={`${isExpanded 
                ? 'w-full flex items-center justify-center space-x-2 h-10 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-300' 
                : 'w-8 h-8 flex items-center justify-center rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-300'
              } transition-all duration-300`}
              title="Ayarlar"
            >
              <FiSettings className="w-5 h-5 flex-shrink-0" />
              {isExpanded && <span className="text-sm truncate min-w-0">Ayarlar</span>}
            </button>
          </div>
        </div>
      </aside>

      {/* Upload Modal */}
      {uploadModalOpen && (
        <DocumentUploadModal
          isOpen={uploadModalOpen}
          onClose={() => setUploadModalOpen(false)}
        />
      )}

      {/* Rename Modal */}
      {renameModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Konuşmayı Yeniden Adlandır
            </h3>
            <input
              type="text"
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              placeholder="Yeni başlık girin..."
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent mb-6"
              maxLength={255}
              autoFocus
              onKeyDown={(e) => {
                if (e.key === 'Enter') confirmRename();
                if (e.key === 'Escape') cancelRename();
              }}
            />
            <div className="flex justify-end space-x-3">
              <button
                onClick={cancelRename}
                className="px-4 py-2 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              >
                İptal
              </button>
              <button
                onClick={confirmRename}
                disabled={!newTitle.trim()}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
              >
                Kaydet
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {deleteConfirmOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              Konuşmayı Sil
            </h3>
            <p className="text-gray-600 dark:text-gray-300 mb-6">
              Bu konuşmayı silmek istediğinizden emin misiniz? Bu işlem geri alınamaz.
            </p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={cancelDelete}
                className="px-4 py-2 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              >
                İptal
              </button>
              <button
                onClick={confirmDelete}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
              >
                Sil
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Settings Modal */}
      <SettingsModal
        isOpen={settingsOpen}
        onClose={() => setSettingsOpen(false)}
      />

      {/* Documents Modal */}
      {documentsModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-4xl mx-4 max-h-[90vh] overflow-y-auto">
            {/* Modal Başlığı */}
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-800 dark:text-white">
                Yüklü Dokümanlar
              </h2>
              <button
                onClick={() => setDocumentsModalOpen(false)}
                className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              >
                <FiX className="w-5 h-5 text-gray-600 dark:text-gray-300" />
              </button>
            </div>

            {/* Doküman Listesi */}
            <div className="space-y-4">
              {documentsLoading ? (
                <div className="flex items-center justify-center py-8">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" />
                    <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                    <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                  </div>
                </div>
              ) : documents.length > 0 ? (
                <div className="space-y-3">
                  {documents.map((document, index) => {
                    const getFileIcon = (filename) => {
                      if (!filename) return FiFile;
                      const ext = filename.split('.').pop()?.toLowerCase();
                      switch (ext) {
                        case 'pdf':
                          return FiFileText;
                        case 'doc':
                        case 'docx':
                          return FiFileText;
                        case 'txt':
                          return FiFileText;
                        default:
                          return FiFile;
                      }
                    };

                    const formatFileSize = (bytes) => {
                      if (!bytes) return 'Bilinmiyor';
                      if (bytes < 1024) return `${bytes} B`;
                      if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
                      return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
                    };

                    const formatDate = (dateString) => {
                      if (!dateString) return 'Bilinmiyor';
                      try {
                        const date = new Date(dateString);
                        return date.toLocaleDateString('tr-TR', {
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric'
                        });
                      } catch {
                        return 'Geçersiz tarih';
                      }
                    };

                    const FileIcon = getFileIcon(document.name || document.filename);

                    return (
                      <div
                        key={document.id || index}
                        className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3 border border-gray-200 dark:border-gray-600"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex items-start space-x-3 flex-1">
                            <FileIcon className="w-6 h-6 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-1" />
                            <div className="flex-1 min-w-0">
                              <h3 className="font-medium text-gray-900 dark:text-white truncate">
                                {document.name || document.filename || `Doküman ${index + 1}`}
                              </h3>
                              
                              {/* Dosya Bilgileri */}
                              <div className="flex items-center gap-4 mt-1 text-sm text-gray-600 dark:text-gray-300">
                                <span>{formatFileSize(document.size || document.file_size)}</span>
                                <span>•</span>
                                <span>{formatDate(document.uploaded_at || document.created_at)}</span>
                              </div>

                                                            {/* Kompakt Ek Bilgiler */}
                              <div className="mt-1 flex flex-wrap gap-1">
                                {document.pages && (
                                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                                    {document.pages} sayfa
                                  </span>
                                )}

                                {document.status && (
                                  <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs ${
                                    document.status === 'processed' || document.status === 'completed'
                                      ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                                      : document.status === 'processing'
                                      ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                                      : 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
                                  }`}>
                                    {document.status === 'processed' || document.status === 'completed' ? 'İşlenmiş' :
                                     document.status === 'processing' ? 'İşleniyor' :
                                     document.status === 'failed' ? 'Başarısız' : document.status}
                                  </span>
                                )}
                              </div>
                            </div>
                          </div>

                          {/* Eylem Butonları */}
                          <div className="flex items-center space-x-2 ml-4">
                            {(document.name || document.filename) && (
                              <>
                                <button
                                  onClick={() => window.open(`${backendUrl}/api/documents/${encodeURIComponent(document.name || document.filename)}`, '_blank')}
                                  className="p-2 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900 text-blue-600 dark:text-blue-400 transition-colors"
                                  title="Görüntüle"
                                >
                                  <FiEye className="w-4 h-4" />
                                </button>
                                <button
                                  onClick={() => {
                                    const link = document.createElement('a');
                                    link.href = `${backendUrl}/api/documents/${encodeURIComponent(document.name || document.filename)}`;
                                    link.download = document.name || document.filename;
                                    link.click();
                                  }}
                                  className="p-2 rounded-lg hover:bg-green-100 dark:hover:bg-green-900 text-green-600 dark:text-green-400 transition-colors"
                                  title="İndir"
                                >
                                  <FiDownload className="w-4 h-4" />
                                </button>
                              </>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="text-center py-8">
                  <FiFile className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                  <p className="text-gray-600 dark:text-gray-400">
                    Henüz doküman yüklenmemiş
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-500 mt-1">
                    Doküman Yükle butonunu kullanarak doküman ekleyebilirsiniz
                  </p>
                </div>
              )}
            </div>

            {/* Modal Alt Kısmı */}
            <div className="flex justify-end mt-6 pt-4 border-t border-gray-200 dark:border-gray-600">
              <button
                onClick={() => setDocumentsModalOpen(false)}
                className="px-4 py-2 bg-gray-200 hover:bg-gray-300 dark:bg-gray-600 dark:hover:bg-gray-500
                  text-gray-800 dark:text-white rounded-lg transition-colors"
              >
                Kapat
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default Sidebar; 