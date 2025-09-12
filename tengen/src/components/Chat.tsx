'use client';

import { useChat } from '@ai-sdk/react';
import { Messages } from './Messages';
import { MultimodalInput } from './MultimodalInput.tsx';

export function Chat() {
  const { messages, input, handleInputChange, handleSubmit } = useChat({
    api: 'http://localhost:8000/code-assist',
  });

  return (
    <div className="flex flex-col w-full max-w-4xl mx-auto py-24">
      <Messages messages={messages} />
      <MultimodalInput
        input={input}
        handleInputChange={handleInputChange}
        handleSubmit={handleSubmit}
      />
    </div>
  );
}