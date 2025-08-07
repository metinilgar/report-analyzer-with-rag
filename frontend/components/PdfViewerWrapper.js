import dynamic from 'next/dynamic';
import { useChat } from '@/contexts/ChatContext';

// PdfViewer'ı dynamic import ile yükle
const PdfViewer = dynamic(() => import('./PdfViewer'), {
  ssr: false,
  loading: () => (
    <div className="fixed top-0 right-0 h-screen w-1/2 
      bg-white dark:bg-gray-800 border-l border-gray-200 dark:border-gray-700 
      flex items-center justify-center z-30 shadow-xl">
      <div className="text-gray-500 dark:text-gray-400">
        PDF Görüntüleyici yükleniyor...
      </div>
    </div>
  )
});

const PdfViewerWrapper = () => {
  const { pdfViewerOpen } = useChat();

  if (!pdfViewerOpen) return null;

  return <PdfViewer />;
};

export default PdfViewerWrapper; 