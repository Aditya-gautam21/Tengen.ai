import { useState, type FormEvent } from 'react';

interface QueryInputProps {
  onSubmit: (topic: string) => void;
}

const QueryInput: React.FC<QueryInputProps> = ({ onSubmit }) => {
  const [topic, setTopic] = useState('');

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (topic.trim()) {
      onSubmit(topic);
      setTopic('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4 max-w-md mx-auto w-full">
      <input
        type="text"
        value={topic}
        onChange={(e) => setTopic(e.target.value)}
        placeholder="Enter a research topic (e.g., AI ethics)"
        className="p-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
      />
      <button
        type="submit"
        disabled={!topic.trim()}
        className="bg-blue-600 text-white p-3 rounded-lg hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 transition disabled:bg-gray-400 dark:disabled:bg-gray-600"
      >
        Start Research
      </button>
    </form>
  );
};

export default QueryInput;
