interface ResultsDisplayProps {
  results: string[];  // Prop for the array of results
}

const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ results }) => {
  if (results.length === 0) return null;  // Hide if no results

  return (
    <div className="mt-6 p-4 bg-gray-100 rounded-lg shadow-md max-w-md mx-auto">
      <h2 className="text-xl font-semibold mb-2">Research Results:</h2>
      <ul className="list-disc pl-5 space-y-2">
        {results.map((item, index) => (
          <li key={index} className="text-gray-700">{item}</li>  // Map over array
        ))}
      </ul>
    </div>
  );
};

export default ResultsDisplay;
