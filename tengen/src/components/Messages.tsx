import type { Message } from '@ai-sdk/react';

export function Messages({ messages }: { messages: Message[] }) {
  return (
    <div className="flex flex-col gap-4 mb-4">
      {messages.map((m, i) => (
        <div key={i} className={`whitespace-pre-wrap flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
          <div className={`inline-block p-3 rounded-lg ${m.role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-200 dark:bg-gray-700'}`}>
            <span className="font-bold block mb-1">{m.role === 'user' ? 'You' : 'AI'}</span>
            {m.content}
          </div>
        </div>
      ))}
    </div>
  );
}