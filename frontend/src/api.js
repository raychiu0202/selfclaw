const API_BASE_URL = 'http://localhost:8000/api';

// ========== 会话管理 ==========

export async function getConversations() {
  const response = await fetch(`${API_BASE_URL}/conversations`);
  if (!response.ok) throw new Error('获取会话列表失败');
  return response.json();
}

export async function createConversation(title = '新对话') {
  const response = await fetch(`${API_BASE_URL}/conversations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title }),
  });
  if (!response.ok) throw new Error('创建会话失败');
  return response.json();
}

export async function deleteConversation(id) {
  const response = await fetch(`${API_BASE_URL}/conversations/${id}`, {
    method: 'DELETE',
  });
  if (!response.ok) throw new Error('删除会话失败');
  return response.json();
}

export async function updateConversation(id, title) {
  const response = await fetch(`${API_BASE_URL}/conversations/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title }),
  });
  if (!response.ok) throw new Error('更新会话失败');
  return response.json();
}

// ========== 消息管理 ==========

export async function getMessages(conversationId) {
  const response = await fetch(`${API_BASE_URL}/conversations/${conversationId}/messages`);
  if (!response.ok) throw new Error('获取消息失败');
  return response.json();
}

// ========== 流式聊天 ==========

export async function streamChat(conversationId, content, onData, onError, onComplete) {
  const response = await fetch(`${API_BASE_URL}/chat/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ conversation_id: conversationId, content }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '发送消息失败');
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const dataStr = line.slice(6);
          try {
            const data = JSON.parse(dataStr);
            if (data.error) {
              onError(data.error);
            } else if (data.done) {
              onComplete();
            } else if (data.type && data.type.startsWith('command_')) {
              // 处理命令状态消息
              onData(data);
            } else if (data.content) {
              // 处理普通聊天内容
              onData(data);
            } else {
              console.warn('收到未知类型的消息:', data);
            }
          } catch (e) {
            console.warn('JSON解析失败，跳过该行:', dataStr, e);
            // 继续处理下一行，不中断流
          }
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}

// ========== 终端命令 ==========

export async function executeCommand(conversationId, command, timeout = 30) {
  const response = await fetch(`${API_BASE_URL}/terminal/execute`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ conversation_id: conversationId, command, timeout }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '执行命令失败');
  }

  return response.json();
}

export async function getCommandHistory(conversationId, limit = 10) {
  const response = await fetch(`${API_BASE_URL}/terminal/history/${conversationId}?limit=${limit}`);
  if (!response.ok) throw new Error('获取命令历史失败');
  return response.json();
}
