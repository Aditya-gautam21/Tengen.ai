import { useState } from 'react';
import { codeAssist } from '../services/api';

const CodeAssist = () => {
  const [prompt, setPrompt] = useState('');
  const [code, setCode] = useState('');
  const [mode, setMode] = useState<'generate' | 'debug'>('generate');
  const [response, setResponse] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const data = await codeAssist(prompt, code, mode);
      setResponse(data.response);
    } catch (error) {
      setResponse('Error during code assistance.');
    }
  };

  return (
    <div className="mt-6 p-4 bg-gray-100 dark:bg-gray-800 rounded-lg shadow-md max-w-md mx-auto w-full">
      <h2 className="text-xl font-semibold mb-2 text-gray-900 dark:text-gray-100">Code Assistant</h2>
      <form onSubmit={handleSubmit}>
        <div className="flex gap-4 mb-4">
          <label>
            <input
              type="radio"
              value="generate"
              checked={mode === 'generate'}
              onChange={() => setMode('generate')}
            />
            Generate
          </label>
          <label>
            <input
              type="radio"
              value="debug"
              checked={mode === 'debug'}
              onChange={() => setMode('debug')}
            />
            Debug
          </label>
        </div>
        {mode === 'generate' ? (
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Enter a prompt to generate code"
            className="p-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 w-full"
          />
        ) : (
          <textarea
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder="Paste code to debug"
            className="p-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 w-full h-32"
          />
        )}
        <button
          type="submit"
          className="bg-blue-600 text-white p-3 rounded-lg hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 transition disabled:bg-gray-400 dark:disabled:bg-gray-600 mt-4 w-full"
        >
          {mode === 'generate' ? 'Generate Code' : 'Debug Code'}
        </button>
      </form>
      {response && (
        <div className="mt-4 p-4 bg-gray-200 dark:bg-gray-700 rounded-lg">
          <h3 className="text-lg font-semibold mb-2">Response:</h3>
          <pre className="whitespace-pre-wrap">{response}</pre>
        </div>
      )}
    </div>
  );
};

export default CodeAssist;