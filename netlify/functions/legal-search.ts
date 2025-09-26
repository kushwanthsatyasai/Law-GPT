import { Handler, HandlerEvent, HandlerContext } from '@netlify/functions';

export const handler: Handler = async (
  event: HandlerEvent,
  context: HandlerContext
) => {
  // Handle CORS preflight
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      },
      body: '',
    };
  }

  // Only allow POST requests
  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
      },
      body: JSON.stringify({ error: 'Method not allowed' }),
    };
  }

  try {
    const { query, court = 'all', max_results = 10 } = JSON.parse(event.body || '{}');

    if (!query) {
      return {
        statusCode: 400,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
        },
        body: JSON.stringify({ error: 'Query parameter is required' }),
      };
    }

    // Check if we have Indian Kanoon API key
    const indianKanoonApiKey = process.env.INDIAN_KANOON_API_KEY;
    
    if (indianKanoonApiKey) {
      // Make actual API call to Indian Kanoon
      const searchUrl = `https://api.indiankanoon.org/search`;
      const searchParams = new URLSearchParams({
        q: query,
        format: 'json',
        api_key: indianKanoonApiKey,
      });

      if (court !== 'all') {
        searchParams.append('court', court);
      }

      const response = await fetch(`${searchUrl}?${searchParams}`, {
        method: 'GET',
        headers: {
          'User-Agent': 'Law-GPT/1.0',
        },
      });

      if (response.ok) {
        const data = await response.json();
        
        const cases = data.results?.slice(0, max_results).map((item: any) => ({
          id: item.doc_id || Math.random().toString(),
          case_id: item.doc_id || '',
          title: item.title || 'Unknown Case',
          court: item.court || court,
          jurisdiction: 'India',
          case_date: item.date || new Date().toISOString().split('T')[0],
          case_type: item.type || 'Civil',
          summary: item.snippet || 'No summary available',
          citation: item.citation || '',
          source: 'indian_kanoon',
          relevance_score: 0.85,
        })) || [];

        return {
          statusCode: 200,
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
          },
          body: JSON.stringify({ cases }),
        };
      }
    }

    // Fallback to mock data
    const mockCases = [
      {
        id: 1,
        case_id: 'MOCK001',
        title: `Sample Case Related to ${query}`,
        court: court === 'all' ? 'Supreme Court of India' : court,
        jurisdiction: 'India',
        case_date: '2023-01-15',
        case_type: 'Civil Appeal',
        summary: `This is a sample legal case related to '${query}'. The case involves important legal principles and precedents that may be relevant to your research. This mock data is provided when external API keys are not configured.`,
        citation: '2023 SCC 123',
        source: 'mock_data',
        relevance_score: 0.85,
      },
      {
        id: 2,
        case_id: 'MOCK002',
        title: `Another Case on ${query}`,
        court: court === 'all' ? 'High Court of Delhi' : court,
        jurisdiction: 'Delhi',
        case_date: '2022-11-20',
        case_type: 'Writ Petition',
        summary: `Another sample case dealing with '${query}'. This demonstrates how the legal system addresses similar issues across different courts and jurisdictions.`,
        citation: '2022 DLH 456',
        source: 'mock_data',
        relevance_score: 0.75,
      },
    ];

    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
      },
      body: JSON.stringify({ cases: mockCases.slice(0, max_results) }),
    };

  } catch (error) {
    console.error('Legal search error:', error);
    
    return {
      statusCode: 500,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
      },
      body: JSON.stringify({ 
        error: 'Internal server error',
        message: 'Failed to search legal cases'
      }),
    };
  }
};
