import { useState } from 'react';
import { FiX, FiUpload, FiFile } from 'react-icons/fi';
import axios from 'axios';

const DocumentUploadModal = ({ isOpen, onClose }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  
  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

  if (!isOpen) return null;

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.type === 'application/pdf') {
        setSelectedFile(file);
        setError('');
      } else {
        setError('Lütfen sadece PDF dosyası seçin.');
        setSelectedFile(null);
      }
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    setError('');
    setSuccess(false);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await axios.post(`${backendUrl}/api/documents/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.status === 'success') {
        setSuccess(true);
        setTimeout(() => {
          onClose();
          setSelectedFile(null);
          setSuccess(false);
        }, 2000);
      } else {
        setError(response.data.message || 'Dosya yüklenirken bir hata oluştu.');
      }
    } catch (error) {
      console.error('Yükleme hatası:', error);
      const errorMessage = error.response?.data?.error || 'Dosya yüklenirken bir hata oluştu. Lütfen tekrar deneyin.';
      setError(errorMessage);
    } finally {
      setUploading(false);
    }
  };

  const handleClose = () => {
    if (!uploading) {
      onClose();
      setSelectedFile(null);
      setError('');
      setSuccess(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full mx-4">
        {/* Modal Başlık */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Doküman Yükle
          </h2>
          <button
            onClick={handleClose}
            disabled={uploading}
            className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 
              transition-colors disabled:opacity-50"
          >
            <FiX className="w-6 h-6 text-gray-600 dark:text-gray-300" />
          </button>
        </div>

        {/* Modal İçerik */}
        <div className="p-6">
          {/* Dosya Seçimi */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              PDF Dosyası Seçin
            </label>
            <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 
              dark:border-gray-600 border-dashed rounded-lg hover:border-gray-400 
              dark:hover:border-gray-500 transition-colors">
              <div className="space-y-1 text-center">
                <FiUpload className="mx-auto h-12 w-12 text-gray-400" />
                <div className="flex text-sm text-gray-600 dark:text-gray-400">
                  <label
                    htmlFor="file-upload"
                    className="relative cursor-pointer rounded-md font-medium 
                      text-blue-600 dark:text-blue-400 hover:text-blue-500 
                      dark:hover:text-blue-300"
                  >
                    <span>Dosya seçin</span>
                    <input
                      id="file-upload"
                      name="file-upload"
                      type="file"
                      className="sr-only"
                      accept=".pdf"
                      onChange={handleFileSelect}
                      disabled={uploading}
                    />
                  </label>
                  <p className="pl-1">veya sürükle bırak</p>
                </div>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Sadece PDF dosyaları
                </p>
              </div>
            </div>
          </div>

          {/* Seçilen Dosya */}
          {selectedFile && (
            <div className="mb-4 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg flex items-center">
              <FiFile className="w-5 h-5 text-gray-500 dark:text-gray-400 mr-2" />
              <span className="text-sm text-gray-700 dark:text-gray-300 truncate">
                {selectedFile.name}
              </span>
              <span className="text-xs text-gray-500 dark:text-gray-400 ml-auto">
                {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
              </span>
            </div>
          )}

          {/* Hata Mesajı */}
          {error && (
            <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 text-red-600 
              dark:text-red-400 rounded-lg text-sm">
              {error}
            </div>
          )}

          {/* Başarı Mesajı */}
          {success && (
            <div className="mb-4 p-3 bg-green-50 dark:bg-green-900/20 text-green-600 
              dark:text-green-400 rounded-lg text-sm">
              Dosya başarıyla yüklendi!
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="flex items-center justify-end space-x-3 px-6 py-4 
          border-t border-gray-200 dark:border-gray-700">
          <button
            onClick={handleClose}
            disabled={uploading}
            className="px-4 py-2 text-gray-700 dark:text-gray-300 
              hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg 
              transition-colors disabled:opacity-50"
          >
            İptal
          </button>
          <button
            onClick={handleUpload}
            disabled={!selectedFile || uploading}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 
              disabled:bg-gray-300 dark:disabled:bg-gray-600 
              text-white rounded-lg transition-colors 
              disabled:cursor-not-allowed"
          >
            {uploading ? 'Yükleniyor...' : 'Yükle'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default DocumentUploadModal; 