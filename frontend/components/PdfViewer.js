import { useState, useEffect } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import { FiX, FiZoomIn, FiZoomOut } from 'react-icons/fi';
import { useChat } from '@/contexts/ChatContext';

// PDF.js worker ayarları
if (typeof window !== 'undefined') {
  pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;
}

const PdfViewer = () => {
  const { pdfViewerOpen, pdfUrl, pdfFileName, closePdfViewer } = useChat();
  const [numPages, setNumPages] = useState(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [scale, setScale] = useState(1.0);
  const [error, setError] = useState(null);

  if (!pdfViewerOpen) return null;

  const onDocumentLoadSuccess = ({ numPages }) => {
    setNumPages(numPages);
    setError(null);
  };

  const onDocumentLoadError = (error) => {
    console.error('PDF yükleme hatası:', error);
    setError('PDF yüklenirken bir hata oluştu.');
  };

  const handleZoomIn = () => {
    setScale(prev => Math.min(prev + 0.1, 3.0));
  };

  const handleZoomOut = () => {
    setScale(prev => Math.max(prev - 0.1, 0.5));
  };

  return (
    <div className="fixed top-0 right-0 h-screen w-1/2 
      bg-white dark:bg-gray-800 border-l border-gray-200 dark:border-gray-700 
      flex flex-col z-30 shadow-xl">
      
      {/* Başlık ve Kontroller */}
      <div className="flex items-center justify-between p-2 border-b border-gray-200 dark:border-gray-700 h-12 bg-white dark:bg-gray-900">
        <div className="flex-1">
          <h3 className="text-base font-semibold text-gray-900 dark:text-white truncate">
            {pdfFileName || 'PDF Görüntüleyici'}
          </h3>
          {numPages && (
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Sayfa {pageNumber} / {numPages}
            </p>
          )}
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={handleZoomOut}
            className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            title="Uzaklaştır"
          >
            <FiZoomOut className="w-4 h-4 text-gray-600 dark:text-gray-300" />
          </button>
          <span className="text-xs text-gray-600 dark:text-gray-300 min-w-[2.5rem] text-center">
            {Math.round(scale * 100)}%
          </span>
          <button
            onClick={handleZoomIn}
            className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            title="Yakınlaştır"
          >
            <FiZoomIn className="w-4 h-4 text-gray-600 dark:text-gray-300" />
          </button>
          <button
            onClick={closePdfViewer}
            className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors ml-2"
            title="Kapat"
          >
            <FiX className="w-4 h-4 text-gray-600 dark:text-gray-300" />
          </button>
        </div>
      </div>

      {/* PDF İçeriği */}
      <div className="flex-1 overflow-auto bg-gray-50 dark:bg-gray-900 p-4 pb-16">
        {error ? (
          <div className="text-center py-8">
            <p className="text-red-600 dark:text-red-400">{error}</p>
          </div>
        ) : (
          <div className="flex justify-center">
            <Document
              file={pdfUrl}
              onLoadSuccess={onDocumentLoadSuccess}
              onLoadError={onDocumentLoadError}
              className="pdf-document"
            >
              <Page
                pageNumber={pageNumber}
                scale={scale}
                className="shadow-lg"
                renderTextLayer={true}
                renderAnnotationLayer={true}
              />
            </Document>
          </div>
        )}
      </div>

      {/* Sayfa Navigasyonu */}
      {numPages && numPages > 1 && (
        <div className="absolute bottom-0 left-0 right-0 flex items-center justify-center p-3 space-x-4">
          <button
            onClick={() => setPageNumber(Math.max(pageNumber - 1, 1))}
            disabled={pageNumber <= 1}
            className="px-3 py-1 rounded bg-gray-200 dark:bg-gray-700 
              hover:bg-gray-300 dark:hover:bg-gray-600 
              disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Önceki
          </button>
          
          <input
            type="number"
            value={pageNumber}
            onChange={(e) => {
              const value = parseInt(e.target.value);
              if (value >= 1 && value <= numPages) {
                setPageNumber(value);
              }
            }}
            className="w-16 px-2 py-1 text-center border border-gray-300 dark:border-gray-600 
              rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            min="1"
            max={numPages}
          />
          
          <button
            onClick={() => setPageNumber(Math.min(pageNumber + 1, numPages))}
            disabled={pageNumber >= numPages}
            className="px-3 py-1 rounded bg-gray-200 dark:bg-gray-700 
              hover:bg-gray-300 dark:hover:bg-gray-600 
              disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Sonraki
          </button>
        </div>
      )}
    </div>
  );
};

export default PdfViewer; 