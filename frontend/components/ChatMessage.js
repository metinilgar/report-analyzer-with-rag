import ReactMarkdown from 'react-markdown';
import { useChat } from '@/contexts/ChatContext';

const ChatMessage = ({ message }) => {
  const { openPdfViewer } = useChat();
  const isUser = message.role === 'user';

  // Özel link renderer - PDF linklerini yakalar
  const customComponents = {
    a: ({ node, href, children, ...props }) => {
      // PDF doküman linki mi kontrol et
      if (href && href.includes('/api/documents/')) {
        const handleClick = (e) => {
          e.preventDefault();
          
          // Dosya adını URL'den çıkar
          const fileName = href.split('/').pop();
          
          // PDF viewer'ı aç ve sidebar'ı kapat
          openPdfViewer({ url: href, fileName });
        };

        return (
          <a
            href={href}
            onClick={handleClick}
            className="text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 
              underline cursor-pointer font-medium"
            {...props}
          >
            {children}
          </a>
        );
      }

      // Normal dış linkler için
      return (
        <a
          href={href}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 
            underline"
          {...props}
        >
          {children}
        </a>
      );
    },
    // Diğer markdown elementleri için özel stiller
    p: ({ children }) => (
      <p className="mb-3 last:mb-0 text-gray-800 dark:text-gray-200 leading-relaxed">
        {children}
      </p>
    ),
    ul: ({ children }) => (
      <ul className="list-disc list-inside mb-3 space-y-1 text-gray-800 dark:text-gray-200">
        {children}
      </ul>
    ),
    ol: ({ children }) => (
      <ol className="list-decimal list-inside mb-3 space-y-1 text-gray-800 dark:text-gray-200">
        {children}
      </ol>
    ),
    li: ({ children }) => (
      <li className="ml-4">{children}</li>
    ),
    h1: ({ children }) => (
      <h1 className="text-2xl font-bold mb-3 text-gray-900 dark:text-gray-100">
        {children}
      </h1>
    ),
    h2: ({ children }) => (
      <h2 className="text-xl font-bold mb-2 text-gray-900 dark:text-gray-100">
        {children}
      </h2>
    ),
    h3: ({ children }) => (
      <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-gray-100">
        {children}
      </h3>
    ),
    code: ({ inline, children }) => {
      if (inline) {
        return (
          <code className="bg-gray-100 dark:bg-gray-800 px-1 py-0.5 rounded text-sm 
            text-gray-800 dark:text-gray-200 font-mono">
            {children}
          </code>
        );
      }
      return (
        <pre className="bg-gray-100 dark:bg-gray-800 p-3 rounded-lg overflow-x-auto mb-3">
          <code className="text-sm text-gray-800 dark:text-gray-200 font-mono">
            {children}
          </code>
        </pre>
      );
    },
    blockquote: ({ children }) => (
      <blockquote className="border-l-4 border-gray-300 dark:border-gray-600 pl-4 italic 
        text-gray-700 dark:text-gray-300 mb-3">
        {children}
      </blockquote>
    ),
  };

  if (isUser) {
    // Kullanıcı mesajı - baloncuk şeklinde
    return (
      <div className="flex justify-end mb-4">
        <div className="bg-blue-600 text-white rounded-lg px-4 py-2 max-w-3xl">
          <p className="whitespace-pre-wrap">{message.content}</p>
        </div>
      </div>
    );
  } else {
    // Sistem cevabı - düz metin şeklinde
    return (
      <div className="mb-6">
        <div className="prose prose-sm dark:prose-invert max-w-none text-gray-900 dark:text-gray-100">
          <ReactMarkdown components={customComponents}>
            {message.content}
          </ReactMarkdown>
        </div>
      </div>
    );
  }
};

export default ChatMessage; 