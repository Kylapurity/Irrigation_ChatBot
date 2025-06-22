import React, { useState, useEffect } from 'react';
import Login from './components/login';
import Chat from './components/chat';

const App = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [authToken, setAuthToken] = useState('');

  // Check for existing session on app load
  useEffect(() => {
    const savedToken = localStorage.getItem('authToken');
    
    if (savedToken) {
      setAuthToken(savedToken);
      setIsLoggedIn(true);
    }
  }, []);

  const handleLogin = (username, token) => {
    setAuthToken(token);
    setIsLoggedIn(true);
    
    // Save to localStorage for session persistence
    localStorage.setItem('authToken', token);
  };

  const handleLogout = () => {
    // Clear local state and storage
    setIsLoggedIn(false);
    setAuthToken('');
    localStorage.removeItem('authToken');
  };

  return (
    <div className="App">
      {isLoggedIn ? (
        <Chat 
          onLogout={handleLogout}
        />
      ) : (
        <Login onLogin={handleLogin} />
      )}
    </div>
  );
};

export default App;