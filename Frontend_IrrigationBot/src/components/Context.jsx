import React, { useState, useEffect, useRef } from 'react';
import { 
  Droplets, 
  Send, 
  History, 
  X, 
  Info, 
  Sprout, 
  Gauge, 
  Settings,
  Menu,
  Plus
} from 'lucide-react';

const irrigationInfo = [
  {
    icon: Gauge,
    title: "Pressure Control",
    description: "Learn optimal water pressure for different irrigation systems and crops"
  },
  {
    icon: Droplets,
    title: "Water Management",
    description: "Efficient water usage techniques and scheduling for better yields"
  },
  {
    icon: Sprout,
    title: "Crop-Specific Care",
    description: "Tailored irrigation advice for tomatoes, maize, vegetables, and more"
  },
  {
    icon: Sprout,
    title: "System Setup",
    description: "Complete guidance on drip, sprinkler, and micro-irrigation systems"
  }
];
const Chat = ({ onLogout }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [showSidebar, setShowSidebar] = useState(true);
  const [activeTab, setActiveTab] = useState('info');
  const [chatHistory, setChatHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (messages.length >= 2) {
      const userMessages = messages.filter(msg => msg.sender === 'user');
      if (userMessages.length > 0) {
        const firstUserMessage = userMessages[0];
        const currentDate = new Date().toISOString().split('T')[0];
        
        const topic = firstUserMessage.text.length > 35 
          ? firstUserMessage.text.substring(0, 35) + '...' 
          : firstUserMessage.text;
        
        const newChatEntry = {
          id: `chat_${Date.now()}`,
          date: currentDate,
          topic: topic,
          preview: firstUserMessage.text,
          messageCount: messages.length,
          lastActive: new Date().toLocaleTimeString()
        };
        
        setChatHistory(prev => {
          const existingIndex = prev.findIndex(chat => 
            chat.topic === topic && chat.date === currentDate
          );
          if (existingIndex >= 0) {
            const updated = [...prev];
            updated[existingIndex] = { ...updated[existingIndex], messageCount: messages.length, lastActive: newChatEntry.lastActive };
            return updated;
          } else {
            return [newChatEntry, ...prev];
          }
        });
      }
    }
  }, [messages]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSendMessage = async () => {
    if (inputMessage.trim() && !isLoading) {
      const userMessage = {
        id: messages.length + 1,
        text: inputMessage,
        sender: 'user',
        timestamp: new Date().toLocaleTimeString()
      };
      
      setMessages(prev => [...prev, userMessage]);
      setInputMessage('');
      setIsLoading(true);

      try {
        // First check if question exists in CSV
        const csvCheck = await checkQuestionInCSV(inputMessage);
        
        if (csvCheck.found) {
          // Question found in CSV, use the answer directly
          const botMessage = {
            id: messages.length + 2,
            text: csvCheck.answer,
            sender: 'bot',
            timestamp: new Date().toLocaleTimeString()
          };
          setMessages(prev => [...prev, botMessage]);
        } else {
          // Question not found in CSV, send to backend
          const response = await fetch('http://127.0.0.1:8000/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: inputMessage })
          });
          
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          
          const data = await response.json();
          const botResponseText = data.response || "No response received";
          
          const botMessage = {
            id: messages.length + 2,
            text: botResponseText,
            sender: 'bot',
            timestamp: new Date().toLocaleTimeString()
          };
          
          setMessages(prev => [...prev, botMessage]);
        }
      } catch (error) {
        console.error('Error sending message:', error);
        const errorMessage = {
          id: messages.length + 2,
          text: "Sorry, I encountered an error. Please try again.",
          sender: 'bot',
          timestamp: new Date().toLocaleTimeString()
        };
        setMessages(prev => [...prev, errorMessage]);
      }
      
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const startNewChat = () => {
    setMessages([]);
    setChatHistory([]);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      {showSidebar && (
        <div className="w-80 bg-white border-r shadow-lg flex flex-col">
          {/* Tab Navigation */}
          <div className="flex border-b">
            <button
              onClick={() => setActiveTab('info')}
              className={`flex-1 py-3 px-4 text-sm font-medium transition-colors ${
                activeTab === 'info'
                  ? 'bg-green-50 text-green-700 border-b-2 border-green-600'
                  : 'text-gray-600 hover:text-green-600'
              }`}
            >
              <Info className="h-4 w-4 inline mr-2" />
              Information
            </button>
            <button
              onClick={() => setActiveTab('history')}
              className={`flex-1 py-3 px-4 text-sm font-medium transition-colors ${
                activeTab === 'history'
                  ? 'bg-green-50 text-green-700 border-b-2 border-green-600'
                  : 'text-gray-600 hover:text-green-600'
              }`}
            >
              <History className="h-4 w-4 inline mr-2" />
              History
            </button>
          </div>

          {/* New Chat Button */}
          <div className="p-4 border-b">
            <button
              onClick={startNewChat}
              className="w-full bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors flex items-center justify-center space-x-2"
            >
              <Plus className="h-4 w-4" />
              <span>New Chat</span>
            </button>
          </div>

          {/* Tab Content */}
          <div className="flex-1 overflow-y-auto">
            {activeTab === 'info' && (
              <div className="p-4 space-y-4">
                <div className="mb-4">
                  <h3 className="font-semibold text-gray-800 mb-2">What I Can Help You With</h3>
                  <p className="text-sm text-gray-600">
                    Get expert advice on irrigation systems, water management, and crop-specific requirements.
                  </p>
                </div>
                
                {irrigationInfo.map((item, index) => {
                  const IconComponent = item.icon;
                  return (
                    <div key={index} className="bg-green-50 p-4 rounded-lg border border-green-100">
                      <div className="flex items-start space-x-3">
                        <div className="bg-green-100 p-2 rounded-lg">
                          <IconComponent className="h-5 w-5 text-green-600" />
                        </div>
                        <div className="flex-1">
                          <h4 className="font-medium text-gray-800 mb-1">{item.title}</h4>
                          <p className="text-sm text-gray-600">{item.description}</p>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            {activeTab === 'history' && (
              <div className="p-4 space-y-3">
                <div className="mb-4">
                  <h3 className="font-semibold text-gray-800 mb-2">Recent Conversations</h3>
                  <p className="text-sm text-gray-600">
                    Your previous irrigation consultations
                  </p>
                </div>
                
                {chatHistory.length > 0 ? (
                  chatHistory.map((chat) => (
                    <div
                      key={chat.id}
                      className="p-3 bg-green-50 rounded-lg hover:bg-green-100 cursor-pointer transition-colors border border-green-100"
                    >
                      <div className="font-medium text-sm text-gray-800 mb-1">
                        {chat.topic}
                      </div>
                      <div className="text-xs text-green-600 mb-2 flex justify-between">
                        <span>{chat.date}</span>
                        <span>{chat.messageCount} messages</span>
                      </div>
                      <div className="text-sm text-gray-600 truncate">
                        {chat.preview}
                      </div>
                      <div className="text-xs text-gray-400 mt-1">
                        Last active: {chat.lastActive}
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <History className="h-12 w-12 mx-auto mb-3 text-gray-300" />
                    <p className="text-sm">No conversations yet</p>
                    <p className="text-xs text-gray-400 mt-1">
                      Start chatting to see your history here
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Logout Button in Sidebar */}
          <div className="p-4 border-t">
            <button
              onClick={onLogout}
              className="w-full text-sm text-red-600 hover:text-red-700 px-3 py-1 rounded-lg hover:bg-red-50 transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      )}

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white shadow-sm border-b px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              {!showSidebar && (
                <button
                  onClick={() => setShowSidebar(true)}
                  className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <Menu className="h-5 w-5" />
                </button>
              )}
              <div className="bg-green-100 w-10 h-10 rounded-full flex items-center justify-center">
                <Droplets className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <h1 className="font-semibold text-gray-800">Shamba Irrigation</h1>
                <p className="text-sm text-gray-500">Online - Ready to help</p>
              </div>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-2xl ${
                  message.sender === 'user'
                    ? 'bg-green-600 text-white'
                    : 'bg-white text-gray-800 shadow-sm border'
                }`}
              >
                <p className="text-sm whitespace-pre-wrap">{message.text}</p>
                <p className={`text-xs mt-1 ${
                  message.sender === 'user' ? 'text-green-100' : 'text-gray-500'
                }`}>
                  {message.timestamp}
                </p>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white text-gray-800 shadow-sm border px-4 py-2 rounded-2xl">
                <div className="flex items-center space-x-2">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                  </div>
                  <span className="text-sm text-gray-500">Typing...</span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="border-t p-4 bg-white">
          <div className="flex space-x-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={isLoading}
              placeholder="Ask about irrigation pressure, crop requirements..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-full focus:ring-2 focus:ring-green-500 focus:border-transparent disabled:opacity-50"
            />
            <button
              onClick={handleSendMessage}
              disabled={isLoading || !inputMessage.trim()}
              className="bg-green-600 text-white p-2 rounded-full hover:bg-green-700 transition-colors disabled:opacity-50"
            >
              <Send className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chat;