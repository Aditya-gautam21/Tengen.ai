import * as React from 'react';

export function MultimodalInput({ input, handleInputChange, handleSubmit }) {
  return (
    <form onSubmit={handleSubmit} className="sticky bottom-0 z-10">
      <div className="relative flex items-center">
        <textarea
          value={input}
          onChange={handleInputChange}
          placeholder="Ask a question..."
          className="w-full p-2 border rounded-lg dark:bg-gray-800"
        />
        <button type="submit" className="absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-full bg-blue-500 text-white">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
          </svg>
        </button>
      </div>
    </form>
  );
}