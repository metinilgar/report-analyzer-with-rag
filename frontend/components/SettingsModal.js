import { useState, useEffect } from 'react';
import { FiX, FiCheckCircle, FiXCircle, FiClock, FiDatabase, FiServer, FiRefreshCw } from 'react-icons/fi';
import axios from 'axios';

const SettingsModal = ({ isOpen, onClose }) => {
  const [healthData, setHealthData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);

  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

  const fetchHealthStatus = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${backendUrl}/health`);
      setHealthData(response.data);
      setLastUpdated(new Date());
    } catch (error) {
      console.error('Sağlık durumu yüklenemedi:', error);
      setHealthData(null);
    } finally {
      setLoading(false);
    }
  };

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    if (isOpen) {
      fetchHealthStatus();
    }
  }, [isOpen]);

  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy':
        return <FiCheckCircle className="w-5 h-5 text-green-500" />;
      case 'unhealthy':
        return <FiXCircle className="w-5 h-5 text-red-500" />;
      default:
        return <FiClock className="w-5 h-5 text-yellow-500" />;
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'healthy':
        return 'Sağlıklı';
      case 'unhealthy':
        return 'Sorunlu';
      default:
        return 'Bilinmiyor';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy':
        return 'text-green-600 dark:text-green-400';
      case 'unhealthy':
        return 'text-red-600 dark:text-red-400';
      default:
        return 'text-yellow-600 dark:text-yellow-400';
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
        {/* Modal Başlığı */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-800 dark:text-white">
            Sistem Ayarları
          </h2>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            <FiX className="w-5 h-5 text-gray-600 dark:text-gray-300" />
          </button>
        </div>

        {/* Sistem Durumu Bölümü */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-800 dark:text-white">
              Sistem Durumu
            </h3>
            <button
              onClick={fetchHealthStatus}
              disabled={loading}
              className="flex items-center space-x-2 px-3 py-2 text-sm
                bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400
                text-white rounded-lg transition-colors
                disabled:cursor-not-allowed"
            >
              <FiRefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              <span>Yenile</span>
            </button>
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-8">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
              </div>
            </div>
          ) : healthData ? (
            <div className="space-y-4">
              {/* Genel Sistem Durumu */}
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    {getStatusIcon(healthData.status)}
                    <div>
                      <h4 className="font-medium text-gray-800 dark:text-white">
                        Genel Sistem Durumu
                      </h4>
                      <p className={`text-sm ${getStatusColor(healthData.status)}`}>
                        {getStatusText(healthData.status)}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      Versiyon: {healthData.version}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {new Date(healthData.timestamp).toLocaleString('tr-TR')}
                    </p>
                  </div>
                </div>
              </div>

              {/* Servis Durumları */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Database Durumu */}
                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                  <div className="flex items-center space-x-3">
                    <FiDatabase className="w-6 h-6 text-gray-600 dark:text-gray-300" />
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-800 dark:text-white">
                        Veritabanı
                      </h4>
                      <div className="flex items-center space-x-2">
                        {getStatusIcon(healthData.services?.database)}
                        <span className={`text-sm ${getStatusColor(healthData.services?.database)}`}>
                          {getStatusText(healthData.services?.database)}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* LightRAG Durumu */}
                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                  <div className="flex items-center space-x-3">
                    <FiServer className="w-6 h-6 text-gray-600 dark:text-gray-300" />
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-800 dark:text-white">
                        LightRAG Servisi
                      </h4>
                      <div className="flex items-center space-x-2">
                        {getStatusIcon(healthData.services?.lightrag)}
                        <span className={`text-sm ${getStatusColor(healthData.services?.lightrag)}`}>
                          {getStatusText(healthData.services?.lightrag)}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Son Güncelleme */}
              {lastUpdated && (
                <div className="text-center">
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Son güncelleme: {lastUpdated.toLocaleString('tr-TR')}
                  </p>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-8">
              <FiXCircle className="w-12 h-12 text-red-500 mx-auto mb-2" />
              <p className="text-red-600 dark:text-red-400">
                Sistem durumu yüklenemedi
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                Backend servisi ile bağlantı kurulamadı
              </p>
            </div>
          )}
        </div>

        {/* Diğer Ayarlar (isteğe bağlı) */}
        <div className="border-t border-gray-200 dark:border-gray-600 pt-6">
          <h3 className="text-lg font-medium text-gray-800 dark:text-white mb-4">
            Diğer Ayarlar
          </h3>
          <div className="text-sm text-gray-600 dark:text-gray-400">
            Gelecekte burada tema tercihi, dil ayarları ve diğer konfigürasyonlar yer alacak.
          </div>
        </div>

        {/* Modal Alt Kısmı */}
        <div className="flex justify-end mt-6 pt-4 border-t border-gray-200 dark:border-gray-600">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-200 hover:bg-gray-300 dark:bg-gray-600 dark:hover:bg-gray-500
              text-gray-800 dark:text-white rounded-lg transition-colors"
          >
            Kapat
          </button>
        </div>
      </div>
    </div>
  );
};

export default SettingsModal; 