import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

export default function Chat({ conversationId }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [streamingMessage, setStreamingMessage] = useState('');
  const [needReplace, setNeedReplace] = useState(false);
  const [commandStatus, setCommandStatus] = useState([]);
  const messagesEndRef = useRef(null);

  // 加载消息历史
  useEffect(() => {
    if (conversationId) {
      loadMessages();
    }
  }, [conversationId]);

  // 自动滚动到底部
  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingMessage]);

  const loadMessages = async () => {
    try {
      const data = await import('./api').then(m => m.getMessages(conversationId));
      setMessages(data);
    } catch (err) {
      setError('加载消息失败: ' + err.message);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading || !conversationId) return;

    const userMessage = input.trim();
    setInput('');
    setError(null);
    setIsLoading(true);
    setStreamingMessage('');
    setNeedReplace(false);
    setCommandStatus([]);

    // 添加用户消息
    setMessages(prev => [...prev, {
      role: 'user',
      content: userMessage,
      id: Date.now()
    }]);

    try {
      const { streamChat } = await import('./api');
      await streamChat(
        conversationId,
        userMessage,
        // onData: 收到数据
        (content) => {
          console.log('收到数据:', content); // 添加调试日志
          // 处理命令状态消息
          if (content.type) {
            console.log('处理命令状态:', content); // 添加调试日志
            setCommandStatus(prev => [...prev, {
              type: content.type,
              command: content.command,
              message: content.message,
              output: content.output,
              error: content.error,
              timestamp: new Date()
            }]);
          } else if (content.content) {
            console.log('处理聊天内容:', content.content); // 添加调试日志
            // 处理普通的聊天内容
            // 检查是否需要替换内容
            if (content.replace) {
              setNeedReplace(true);
            }
            setStreamingMessage(prev => prev + content.content);
          } else {
            // 忽略没有content的消息
            console.warn('收到没有content字段的消息:', content);
          }
        },
        // onError: 发生错误
        (errorMessage) => {
          setError(errorMessage);
          setIsLoading(false);
        },
        // onComplete: 完成
        () => {
          console.log('流式传输完成'); // 添加调试日志
          console.log('最终流式消息:', streamingMessage); // 添加调试日志
          console.log('是否需要替换:', needReplace); // 添加调试日志
          // 将流式消息添加到消息列表，避免内容消失
          if (streamingMessage.trim()) {
            console.log('添加AI回复到消息列表'); // 添加调试日志
            setMessages(prev => [...prev, {
              role: 'assistant',
              content: streamingMessage,
              id: Date.now()
            }]);
          }
          // 如果需要替换，重新加载消息以获取完整的历史
          if (needReplace) {
            loadMessages();
          }
          setIsLoading(false);
          setStreamingMessage('');
          setNeedReplace(false);
          // 不清空命令状态，让它们保留在界面上
          // setCommandStatus([]);
        }
      );
    } catch (err) {
      setError(err.message);
      setIsLoading(false);
      setStreamingMessage('');
      setNeedReplace(false);
    }
  };

  const handleStop = () => {
    setIsLoading(false);
    setStreamingMessage('');
    setError('已停止生成');
  };

  const handleRegenerate = async () => {
    if (isLoading || !conversationId) return;
    const lastUserMessage = [...messages].reverse().find(m => m.role === 'user');
    if (lastUserMessage) {
      // 移除最后一条用户消息和之后的消息
      const lastUserIndex = messages.findIndex(m => m.id === lastUserMessage.id);
      const newMessages = messages.slice(0, lastUserIndex);
      setMessages(newMessages);
      // 重新发送
      setInput(lastUserMessage.content);
      setTimeout(() => handleSend({ preventDefault: () => {} }), 0);
    }
  };

  const handleCopy = (text) => {
    navigator.clipboard.writeText(text);
    // 可以添加提示
  };

  const MessageComponent = ({ message }) => (
    <div className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-[70%] rounded-lg p-4 ${
        message.role === 'user'
          ? 'bg-blue-500 text-white'
          : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100'
      }`}>
        <div className="flex justify-between items-start mb-2">
          <span className="text-xs font-semibold uppercase opacity-70">
            {message.role === 'user' ? '你' : 'AI'}
          </span>
          {message.role === 'assistant' && (
            <button
              onClick={() => handleCopy(message.content)}
              className="text-xs opacity-50 hover:opacity-100"
            >
              复制
            </button>
          )}
        </div>
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={{
            code({ node, inline, className, children, ...props }) {
              const match = /language-(\w+)/.exec(className || '');
              return !inline && match ? (
                <div className="relative">
                  <SyntaxHighlighter
                    style={vscDarkPlus}
                    language={match[1]}
                    PreTag="div"
                    {...props}
                  >
                    {String(children).replace(/\n$/, '')}
                  </SyntaxHighlighter>
                  <button
                    onClick={() => handleCopy(String(children))}
                    className="absolute top-2 right-2 text-xs bg-gray-700 text-white px-2 py-1 rounded opacity-50 hover:opacity-100"
                  >
                    复制
                  </button>
                </div>
              ) : (
                <code className={className} {...props}>
                  {children}
                </code>
              );
            },
          }}
        >
          {message.content}
        </ReactMarkdown>
      </div>
    </div>
  );

  return (
    <div className="flex flex-col h-full">
      {/* 消息列表 */}
      <div className="flex-1 overflow-y-auto p-4">
        {messages.length === 0 && !isLoading && (
          <div className="text-center text-gray-500 dark:text-gray-400 mt-20">
            <p className="text-xl mb-2">👋 开始新的对话</p>
            <p>输入问题，让GLM-5为你解答</p>
          </div>
        )}

        {messages.map(message => (
          <MessageComponent key={message.id} message={message} />
        ))}

        {/* 命令执行状态显示 */}
        {commandStatus.map((status, index) => (
          <div key={`command-${index}`} className="flex justify-start mb-4">
            <div className="max-w-[70%] rounded-lg p-4 bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xs font-semibold uppercase opacity-70">系统</span>
                {status.type === 'command_start' && <span className="text-yellow-500">⏳</span>}
                {status.type === 'command_success' && <span className="text-green-500">✅</span>}
                {status.type === 'command_error' && <span className="text-red-500">❌</span>}
              </div>
              <div className="text-sm">
                <div className="font-mono bg-gray-200 dark:bg-gray-700 p-2 rounded mb-2">
                  {status.command}
                </div>
                <div>{status.message}</div>
                {status.output && (
                  <div className="mt-2 p-2 bg-gray-200 dark:bg-gray-700 rounded font-mono text-xs">
                    {status.output}
                  </div>
                )}
                {status.error && (
                  <div className="mt-2 p-2 bg-red-100 dark:bg-red-900 rounded text-red-700 dark:text-red-300 text-xs">
                    {status.error}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}

        {streamingMessage && (
          <MessageComponent
            message={{
              role: 'assistant',
              content: streamingMessage,
              id: 'streaming'
            }}
          />
        )}

        {error && (
          <div className="flex justify-center mb-4">
            <div className="bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 px-4 py-2 rounded-lg">
              {error}
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* 输入框 */}
      <div className="border-t border-gray-200 dark:border-gray-700 p-4">
        <form onSubmit={handleSend} className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="输入你的问题..."
            disabled={isLoading || !conversationId}
            className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
          />
          {isLoading ? (
            <button
              type="button"
              onClick={handleStop}
              className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
            >
              停止
            </button>
          ) : (
            <button
              type="submit"
              disabled={!conversationId}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 dark:disabled:bg-gray-600"
            >
              发送
            </button>
          )}
        </form>

        {messages.length > 0 && !isLoading && (
          <div className="mt-2 text-center">
            <button
              onClick={handleRegenerate}
              className="text-sm text-blue-500 hover:text-blue-600"
            >
              重新生成
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
