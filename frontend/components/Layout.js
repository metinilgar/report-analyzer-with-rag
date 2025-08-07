import Header from './Header';
import Sidebar from './Sidebar';
import { useChat } from '@/contexts/ChatContext';

const Layout = ({ children }) => {
  const { sidebarOpen, pdfViewerOpen } = useChat();

  return (
    <div className="flex flex-col h-screen bg-gray-50 dark:bg-gray-900">
      <Header />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main
          className={`
            flex-1 transition-all duration-300
            ${sidebarOpen ? 'ml-64' : 'ml-12'}
            ${pdfViewerOpen ? 'mr-[50%]' : 'mr-0'}
          `}
        >
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout; 