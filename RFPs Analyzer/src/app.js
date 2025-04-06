import React, { useState } from "react";
import UploadForm from "./components/UploadForm";
import "./App.css";

const App = () => {
  const [darkMode, setDarkMode] = useState(false);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    document.body.className = darkMode ? "light-mode" : "dark-mode";
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Contract IQ</h1>
        <nav>
          <a href="#dashboard">Dashboard</a>
          <a href="#history">History</a>
          <a href="#help">Help</a>
        </nav>
        <button onClick={toggleDarkMode} className="mode-toggle">
          {darkMode ? "Light Mode" : "Dark Mode"}
        </button>
      </header>
      <main>
        <UploadForm />
      </main>
    </div>
  );
};

export default App;
