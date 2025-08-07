import Layout from '@/components/Layout';
import ChatContainer from '@/components/ChatContainer';
import PdfViewerWrapper from '@/components/PdfViewerWrapper';
import { ChatProvider } from '@/contexts/ChatContext';
import { ThemeProvider } from '@/contexts/ThemeContext';
import Head from 'next/head';

export default function Home() {
  return (
    <ThemeProvider>
      <ChatProvider>
        <Head>
          <title>Rapor Analiz Asistanı</title>
          <meta name="description" content="Raporları sorgulayın ve inceleyin" />
          <link rel="icon" href="/favicon.ico" />
        </Head>
        
        <Layout>
          <ChatContainer />
          <PdfViewerWrapper />
        </Layout>
      </ChatProvider>
    </ThemeProvider>
  );
}
