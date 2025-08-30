interface ResultsDisplayProps {
  results: string[];
}

const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ results }) => {
  if (results.length === 0) return null;

  return (
    <div className="mt-6 p-4 bg-gray-100 dark:bg-gray-800 rounded-lg shadow-md max-w-md mx-auto w-full">
      <h2 className="text-xl font-semibold mb-2 text-gray-900 dark:text-gray-100">Research Results:</h2>
      <ul className="list-disc pl-5 space-y-2 text-gray-700 dark:text-gray-300">
        {results.map((item, index) => (
          <li key={index}>{item}</li>
        ))}
      </ul>
    </div>
  );
};

export default ResultsDisplay;
