import { ResearchPanel } from '@/components/research-panel';

export default function Page() {
  return (
    <div className="container mx-auto py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Tengen.ai Research Assistant
          </h1>
          <p className="text-lg text-gray-600">
            Your intelligent research companion for discovering and analyzing information
          </p>
        </div>
        
        <ResearchPanel />
      </div>
    </div>
  );
}
