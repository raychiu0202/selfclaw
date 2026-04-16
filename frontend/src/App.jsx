import React, { useState, useEffect } from 'react';
import Sidebar from './Sidebar';
import Chat from './Chat';
import { getConversations, createConversation, deleteConversation, updateConversation } from './api';
import './App.css';

function App() {
  const [conversations, setConversations] = useState([]);
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [loading, setLoading] = useState(true);

  // 加载会话列表
  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      setLoading(true);
      const data = await getConversations();
      setConversations(data.conversations || []);
      // 如果没有会话，自动创建一个
      if (!data.conversations || data.conversations.length === 0) {
        await handleCreateConversation();
      } else if (!currentConversationId) {
        // 如果当前没有选中的会话，选中第一个
        setCurrentConversationId(data.conversations[0].id);
      }
    } catch (err) {
      console.error('加载会话失败:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateConversation = async () => {
    try {
      const newConversation = await createConversation(`对话 ${new Date().toLocaleString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}`);
      setConversations(prev => [newConversation, ...prev]);
      setCurrentConversationId(newConversation.id);
    } catch (err) {
      console.error('创建会话失败:', err);
      alert('创建会话失败，请检查后端服务是否正常运行');
    }
  };

  const handleDeleteConversation = async (id) => {
    try {
      await deleteConversation(id);
      setConversations(prev => prev.filter(c => c.id !== id));
      // 如果删除的是当前会话，选中另一个
      if (id === currentConversationId) {
        const remaining = conversations.filter(c => c.id !== id);
        if (remaining.length > 0) {
          setCurrentConversationId(remaining[0].id);
        } else {
          // 如果没有会话了，创建新的
          await handleCreateConversation();
        }
      }
    } catch (err) {
      console.error('删除会话失败:', err);
      alert('删除会话失败');
    }
  };

  const handleUpdateConversation = async (id, title) => {
    try {
      const updated = await updateConversation(id, title);
      setConversations(prev => prev.map(c => c.id === id ? updated : c));
    } catch (err) {
      console.error('更新会话失败:', err);
      alert('更新会话失败');
    }
  };

  const handleSelectConversation = (conversation) => {
    setCurrentConversationId(conversation.id);
  };

  return (
    <div className="h-screen w-screen bg-white dark:bg-gray-950 text-gray-900 dark:text-gray-100">
      <div className="flex h-full">
        <Sidebar
          conversations={conversations}
          currentConversationId={currentConversationId}
          onSelectConversation={handleSelectConversation}
          onCreateConversation={handleCreateConversation}
          onDeleteConversation={handleDeleteConversation}
          onUpdateConversation={handleUpdateConversation}
        />
        <div className="flex-1">
          {currentConversationId ? (
            <Chat conversationId={currentConversationId} />
          ) : (
            <div className="flex items-center justify-center h-full">
              {loading ? '加载中...' : '请选择或创建一个会话'}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
