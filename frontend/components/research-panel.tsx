'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Loader2, Search, ExternalLink } from 'lucide-react';
import { tengenAPI, type ResearchResponse } from '@/lib/api';

export function ResearchPanel() {
  const [topic, setTopic] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<ResearchResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleResearch = async () => {
    if (!topic.trim()) return;

    setIsLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await tengenAPI.research(topic, 5);
      setResults(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Research failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !isLoading) {
      handleResearch();
    }
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5" />
            Research Assistant
          </CardTitle>
          <CardDescription>
            Enter a topic to research and gather information from the web
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Input
              placeholder="Enter research topic (e.g., 'artificial intelligence', 'climate change')"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={isLoading}
            />
            <Button 
              onClick={handleResearch} 
              disabled={isLoading || !topic.trim()}
            >
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Search className="h-4 w-4" />
              )}
              Research
            </Button>
          </div>

          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-md text-red-700">
              Error: {error}
            </div>
          )}

          {results && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">Research Results for "{results.topic}"</h3>
                <Badge variant={results.status === 'completed' ? 'default' : 'destructive'}>
                  {results.status}
                </Badge>
              </div>

              <p className="text-sm text-gray-600">{results.message}</p>

              {results.results_count && (
                <p className="text-sm text-gray-500">
                  Found {results.results_count} sources
                </p>
              )}

              <div className="space-y-3">
                {results.sources.map((source, index) => (
                  <Card key={index} className="border-l-4 border-l-blue-500">
                    <CardContent className="pt-4">
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex-1">
                          <h4 className="font-medium text-sm mb-1">{source.title}</h4>
                          <p className="text-xs text-gray-600 mb-2">{source.summary}</p>
                          <a
                            href={source.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800"
                          >
                            <ExternalLink className="h-3 w-3" />
                            View Source
                          </a>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}