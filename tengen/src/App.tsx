import { useState, useEffect } from 'react';
import QueryInput from './components/QueryInput';
import ResultsDisplay from './components/ResultsDisplay';
import { scrapeResearch } from './services/api';
import ChatWidget from "./components/ChatWidget.tsx";

function App() {
  const [results, setResults] = useState<string[]>([]);
  const [isDarkMode, setIsDarkMode] = useState(true);

  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  const handleSubmit = async (topic: string) => {
    try {
      const data = await scrapeResearch(topic);
      setResults(data.map((item: { content: any }) => item.content));
    } catch (error) {
      setResults(['Error during scraping']);
    }
  };

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex flex-col items-center justify-center p-4 text-gray-900 dark:text-gray-100">
      <h1 className="text-3xl font-bold mb-6 text-blue-800 dark:text-blue-300">
        Tengen.ai Research Assistant
      </h1>

      {/* Old input/output UI (optional – can be removed if you want only chatbot) */}
      <QueryInput onSubmit={handleSubmit} />
      <ResultsDisplay results={results} />

      <button
        onClick={toggleDarkMode}
        className="mt-4 bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-gray-100 px-4 py-2 rounded hover:bg-gray-300 dark:hover:bg-gray-600 transition"
      >
        {isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
      </button>

      <ChatWidget />
    </div>
  );
}

export default App;
