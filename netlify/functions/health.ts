import { Handler, HandlerEvent, HandlerContext } from '@netlify/functions';

export const handler: Handler = async (
  event: HandlerEvent,
  context: HandlerContext
) => {
  // Only allow GET requests
  if (event.httpMethod !== 'GET') {
    return {
      statusCode: 405,
      body: JSON.stringify({ error: 'Method not allowed' }),
    };
  }

  try {
    const healthData = {
      status: 'ok',
      timestamp: new Date().toISOString(),
      service: 'Law-GPT Netlify Functions',
      version: '1.0.0',
      environment: process.env.NODE_ENV || 'development',
      api_keys: {
        google_api_key: !!process.env.GOOGLE_API_KEY,
        indian_kanoon_api_key: !!process.env.INDIAN_KANOON_API_KEY,
      }
    };

    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
      },
      body: JSON.stringify(healthData),
    };
  } catch (error) {
    console.error('Health check error:', error);
    
    return {
      statusCode: 500,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
      },
      body: JSON.stringify({ 
        status: 'error', 
        message: 'Internal server error' 
      }),
    };
  }
};
