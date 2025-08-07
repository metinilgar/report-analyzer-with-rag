import { useChat } from '@/contexts/ChatContext';

const Header = () => {
  const { sidebarOpen } = useChat();
  
      return (
      <header className={`
        h-12 transition-all duration-300 hidden
        ${sidebarOpen ? 'ml-64' : 'ml-12'}
      `}>
      </header>
    );
};

export default Header; 