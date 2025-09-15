import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const API_BASE = '/api';

interface LegalCase {
  id: number;
  case_id: string;
  title: string;
  court: string;
  jurisdiction: string;
  case_date?: string;
  case_type: string;
  summary: string;
  citation: string;
  source: string;
  relevance_score?: number;
}

interface LegalStatute {
  id: number;
  statute_id: string;
  title: string;
  jurisdiction: string;
  section_number?: string;
  summary: string;
  effective_date?: string;
  source: string;
  relevance_score?: number;
}

interface Court {
  id: string;
  name: string;
}

interface Jurisdiction {
  id: string;
  name: string;
}

const IndianLegalResearch: React.FC = () => {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [selectedCourt, setSelectedCourt] = useState('all');
  const [selectedJurisdiction, setSelectedJurisdiction] = useState('all');
  const [searchType, setSearchType] = useState<'cases' | 'statutes' | 'both'>('both');
  const [results, setResults] = useState<{
    cases: LegalCase[];
    statutes: LegalStatute[];
    total_results: number;
  }>({ cases: [], statutes: [], total_results: 0 });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [courts, setCourts] = useState<Court[]>([]);
  const [jurisdictions, setJurisdictions] = useState<Jurisdiction[]>([]);

  useEffect(() => {
    loadCourtsAndJurisdictions();
  }, []);

  const loadCourtsAndJurisdictions = async () => {
    try {
      const [courtsRes, jurisdictionsRes] = await Promise.all([
        fetch(`${API_BASE}/indian-legal/courts`),
        fetch(`${API_BASE}/indian-legal/jurisdictions`)
      ]);

      if (courtsRes.ok) {
        const courtsData = await courtsRes.json();
        setCourts(courtsData);
      }

      if (jurisdictionsRes.ok) {
        const jurisdictionsData = await jurisdictionsRes.json();
        setJurisdictions(jurisdictionsData);
      }
    } catch (err) {
      console.error('Failed to load courts and jurisdictions:', err);
    }
  };

  const searchIndianLegal = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('You must be logged in to search legal databases');
      }

      let cases: LegalCase[] = [];
      let statutes: LegalStatute[] = [];

      if (searchType === 'cases' || searchType === 'both') {
        const casesRes = await fetch(`${API_BASE}/indian-legal/cases/search`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            Authorization: `Bearer ${token}`
          },
          body: new URLSearchParams({
            query: query,
            court: selectedCourt,
            max_results: '10'
          })
        });

        if (casesRes.ok) {
          const casesData = await casesRes.json();
          cases = casesData.cases || [];
        }
      }

      if (searchType === 'statutes' || searchType === 'both') {
        const statutesRes = await fetch(`${API_BASE}/indian-legal/statutes/search`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            Authorization: `Bearer ${token}`
          },
          body: new URLSearchParams({
            query: query,
            jurisdiction: selectedJurisdiction,
            max_results: '10'
          })
        });

        if (statutesRes.ok) {
          const statutesData = await statutesRes.json();
          statutes = statutesData.statutes || [];
        }
      }

      setResults({
        cases,
        statutes,
        total_results: cases.length + statutes.length
      });
    } catch (err: any) {
      setError('Search failed: ' + (err.message || 'Unknown error'));
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      searchIndianLegal();
    }
  };

  const getSourceColor = (source: string) => {
    switch (source) {
      case 'indian_kanoon':
        return 'bg-blue-100 text-blue-800';
      case 'scc_online':
        return 'bg-green-100 text-green-800';
      case 'kanoon_dev':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getRelevanceColor = (score?: number) => {
    if (!score) return 'text-gray-500';
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Header */}
      <div className="bg-gray-800 shadow-sm border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div>
              <h1 className="text-2xl font-bold text-green-400">Indian Legal Research</h1>
              <p className="text-gray-300">Search Indian case law, statutes, and legal precedents</p>
            </div>
            <button
              onClick={() => navigate('/dashboard')}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              Back to Dashboard
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search Form */}
        <div className="bg-gray-800 rounded-lg shadow-sm p-6 mb-6 border border-gray-700">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Search Query
              </label>
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Enter your legal research query (e.g., 'employment termination', 'contract breach')"
                className="w-full px-3 py-2 border border-gray-600 rounded-md bg-gray-700 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Search Type
                </label>
                <select
                  value={searchType}
                  onChange={(e) => setSearchType(e.target.value as 'cases' | 'statutes' | 'both')}
                  className="w-full px-3 py-2 border border-gray-600 rounded-md bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  <option value="both">Cases & Statutes</option>
                  <option value="cases">Cases Only</option>
                  <option value="statutes">Statutes Only</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Court
                </label>
                <select
                  value={selectedCourt}
                  onChange={(e) => setSelectedCourt(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-600 rounded-md bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  {courts.map(court => (
                    <option key={court.id} value={court.id}>{court.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Jurisdiction
                </label>
                <select
                  value={selectedJurisdiction}
                  onChange={(e) => setSelectedJurisdiction(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-600 rounded-md bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  {jurisdictions.map(jurisdiction => (
                    <option key={jurisdiction.id} value={jurisdiction.id}>{jurisdiction.name}</option>
                  ))}
                </select>
              </div>
            </div>

            <button
              onClick={searchIndianLegal}
              disabled={!query.trim() || loading}
              className="w-full md:w-auto px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'Searching...' : 'Search Indian Legal Database'}
            </button>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-900/20 border border-red-500 rounded-lg p-4 mb-6">
            <div className="flex">
              <div className="text-red-400">
                <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-300">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Results */}
        {results.total_results > 0 && (
          <div className="space-y-6">
            {/* Summary */}
            <div className="bg-gray-800 rounded-lg shadow-sm p-6 border border-gray-700">
              <h3 className="text-lg font-semibold text-green-400 mb-2">Search Results</h3>
              <p className="text-gray-300">
                Found {results.total_results} results for "{query}"
                {results.cases.length > 0 && ` (${results.cases.length} cases`}
                {results.statutes.length > 0 && `, ${results.statutes.length} statutes`}
                {results.cases.length > 0 || results.statutes.length > 0 ? ')' : ''}
              </p>
            </div>

            {/* Cases */}
            {results.cases.length > 0 && (
              <div className="bg-gray-800 rounded-lg shadow-sm p-6 border border-gray-700">
                <h3 className="text-lg font-semibold text-green-400 mb-4">Legal Cases</h3>
                <div className="space-y-4">
                  {results.cases.map((case_item, index) => (
                    <div key={index} className="border border-gray-600 rounded-lg p-4 hover:bg-gray-700 transition-colors">
                      <div className="flex justify-between items-start mb-2">
                        <h4 className="text-lg font-medium text-white">{case_item.title}</h4>
                        <div className="flex space-x-2">
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getSourceColor(case_item.source)}`}>
                            {case_item.source}
                          </span>
                          {case_item.relevance_score && (
                            <span className={`text-xs font-medium ${getRelevanceColor(case_item.relevance_score)}`}>
                              {Math.round(case_item.relevance_score * 100)}% match
                            </span>
                          )}
                        </div>
                      </div>
                      
                      <div className="text-sm text-gray-300 mb-2">
                        <p><strong>Court:</strong> {case_item.court}</p>
                        <p><strong>Citation:</strong> {case_item.citation}</p>
                        {case_item.case_date && (
                          <p><strong>Date:</strong> {new Date(case_item.case_date).toLocaleDateString()}</p>
                        )}
                      </div>
                      
                      <p className="text-sm text-gray-200">{case_item.summary}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Statutes */}
            {results.statutes.length > 0 && (
              <div className="bg-gray-800 rounded-lg shadow-sm p-6 border border-gray-700">
                <h3 className="text-lg font-semibold text-green-400 mb-4">Legal Statutes</h3>
                <div className="space-y-4">
                  {results.statutes.map((statute, index) => (
                    <div key={index} className="border border-gray-600 rounded-lg p-4 hover:bg-gray-700 transition-colors">
                      <div className="flex justify-between items-start mb-2">
                        <h4 className="text-lg font-medium text-white">{statute.title}</h4>
                        <div className="flex space-x-2">
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getSourceColor(statute.source)}`}>
                            {statute.source}
                          </span>
                          {statute.relevance_score && (
                            <span className={`text-xs font-medium ${getRelevanceColor(statute.relevance_score)}`}>
                              {Math.round(statute.relevance_score * 100)}% match
                            </span>
                          )}
                        </div>
                      </div>
                      
                      <div className="text-sm text-gray-300 mb-2">
                        <p><strong>Jurisdiction:</strong> {statute.jurisdiction}</p>
                        {statute.section_number && (
                          <p><strong>Section:</strong> {statute.section_number}</p>
                        )}
                        {statute.effective_date && (
                          <p><strong>Effective Date:</strong> {new Date(statute.effective_date).toLocaleDateString()}</p>
                        )}
                      </div>
                      
                      <p className="text-sm text-gray-200">{statute.summary}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* No Results */}
        {!loading && query && results.total_results === 0 && (
          <div className="bg-gray-800 rounded-lg shadow-sm p-6 text-center border border-gray-700">
            <div className="text-6xl mb-4">🔍</div>
            <h3 className="text-lg font-semibold text-green-400 mb-2">No Results Found</h3>
            <p className="text-gray-300 mb-4">
              No legal cases or statutes found for your query. Try different keywords or search terms.
            </p>
            <button
              onClick={() => setQuery('')}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              Clear Search
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default IndianLegalResearch;
