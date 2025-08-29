import {useState, type FormEvent} from 'react';
import * as React from "react";

interface QueryInputProps {onSubmit: (topic: string) => void;}


    const QueryInput:React.FC<QueryInputProps> = ({onSubmit}) => {
    const[topic, setTopic] = useState('');
    const handleSubmit= (e: FormEvent) =>{
        e.preventDefault();
        if(topic.trim()){
            onSubmit(topic);
            setTopic('');
        }
        };
    return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4 max-w-md mx-auto">
      <input
        type="text"
        value={topic}
        onChange={(e) => setTopic(e.target.value)}  // Update state on type
        placeholder="Enter a research topic (e.g., AI ethics)"
        className="p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      <button
        type="submit"
        disabled={!topic.trim()}  // Disable if empty
        className="bg-blue-600 text-black p-3 rounded-lg hover:bg-blue-700 transition disabled:bg-gray-400"
      >
        Start Research
      </button>
    </form>
  );
};


export default QueryInput;