import { useState, useEffect } from 'react';
import axios from 'axios';

// ── Component 1: Error Type Badge ──
function ErrorTypeBadge({ errorType }) {
  const config = {
    timeout:   { color: 'bg-orange-500', icon: '⏱️' },
    locator:   { color: 'bg-red-500',    icon: '🔍' },
    assertion: { color: 'bg-yellow-500', icon: '❗' },
    network:   { color: 'bg-purple-500', icon: '🌐' },
    unknown:   { color: 'bg-gray-500',   icon: '❓' },
  };
  const { color, icon } = config[errorType] || config.unknown;
  return (
    <span className={`${color} text-white text-xs font-bold px-3 py-1 rounded-full uppercase flex items-center gap-1`}>
      {icon} {errorType}
    </span>
  );
}

// ── Component 2: Loading Skeleton ──
function LoadingSkeleton() {
  return (
    <div className="bg-slate-800 border border-slate-600 rounded-xl p-6 mt-6 space-y-4 animate-pulse">
      <div className="flex items-center gap-3">
        <div className="h-6 w-24 bg-slate-600 rounded-full"></div>
        <div className="h-4 w-32 bg-slate-700 rounded ml-auto"></div>
      </div>
      <div>
        <div className="h-3 w-24 bg-slate-600 rounded mb-2"></div>
        <div className="h-4 w-full bg-slate-700 rounded mb-1"></div>
        <div className="h-4 w-3/4 bg-slate-700 rounded"></div>
      </div>
      <div>
        <div className="h-3 w-28 bg-slate-600 rounded mb-2"></div>
        <div className="h-16 w-full bg-slate-900 rounded-lg border border-slate-700"></div>
      </div>
      <div className="flex items-center gap-2">
        <div className="h-3 w-20 bg-slate-600 rounded"></div>
        <div className="h-4 w-12 bg-slate-700 rounded"></div>
      </div>
    </div>
  );
}

// ── Component 3: Copy Button ──
function CopyButton({ text }) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000); // reset after 2s
    } catch {
      alert('Copy failed — please copy manually');
    }
  }

  return (
    <button
      onClick={handleCopy}
      className="text-xs px-2 py-1 rounded bg-slate-700 hover:bg-slate-600 text-slate-300 hover:text-white transition-colors"
    >
      {copied ? '✅ Copied!' : '📋 Copy'}
    </button>
  );
}

// ── Component 4: Result Card ──
function ResultCard({ result }) {
  const confColour = {
    high:   'text-green-400',
    medium: 'text-yellow-400',
    low:    'text-red-400',
  };
  const confBar = { high: 'w-full', medium: 'w-2/3', low: 'w-1/3' };

  return (
    <div className="bg-slate-800 border border-slate-600 rounded-xl p-6 mt-6 space-y-4">

      {/* Header */}
      <div className="flex items-center justify-between">
        <ErrorTypeBadge errorType={result.error_type} />
        {result.is_flaky && (
          <span className="text-yellow-400 text-sm font-semibold">
            ⚠️ Possibly Flaky
          </span>
        )}
      </div>

      {/* Test name if present */}
      {result.test_name && (
        <p className="text-slate-400 text-xs">
          📝 Test: <span className="text-slate-200">{result.test_name}</span>
        </p>
      )}

      {/* Root Cause */}
      <div>
        <p className="text-slate-400 text-xs uppercase font-bold mb-1">🔍 Root Cause</p>
        <p className="text-white text-sm leading-relaxed">{result.root_cause}</p>
      </div>

      {/* Fix with Copy button */}
      <div>
        <div className="flex items-center justify-between mb-1">
          <p className="text-slate-400 text-xs uppercase font-bold">🔧 Suggested Fix</p>
          <CopyButton text={result.fix} />
        </div>
        <div className="bg-slate-900 rounded-lg p-3 border border-slate-700">
          <p className="text-green-300 text-sm font-mono whitespace-pre-wrap">{result.fix}</p>
        </div>
      </div>

      {/* Confidence meter */}
      <div>
        <div className="flex items-center justify-between mb-1">
          <p className="text-slate-400 text-xs uppercase font-bold">✅ Confidence</p>
          <p className={`text-sm font-bold uppercase ${confColour[result.confidence]}`}>
            {result.confidence}
          </p>
        </div>
        <div className="w-full bg-slate-700 rounded-full h-1.5">
          <div className={`${confBar[result.confidence]} h-1.5 rounded-full ${
            result.confidence === 'high' ? 'bg-green-400' :
            result.confidence === 'medium' ? 'bg-yellow-400' : 'bg-red-400'
          }`}></div>
        </div>
      </div>

    </div>
  );
}

// ── Component 5: History Item ──
function HistoryItem({ item, onSelect }) {
  const colours = {
    timeout: 'border-orange-500', locator: 'border-red-500',
    assertion: 'border-yellow-500', network: 'border-purple-500',
    unknown: 'border-gray-500'
  };
  return (
    <button
      onClick={() => onSelect(item)}
      className={`w-full text-left bg-slate-800 border-l-4 ${colours[item.error_type] || 'border-gray-500'} 
        rounded-r-lg p-3 hover:bg-slate-700 transition-colors`}
    >
      <div className="flex items-center justify-between">
        <span className="text-white text-xs font-semibold uppercase">{item.error_type}</span>
        <span className="text-slate-500 text-xs">{item.timestamp}</span>
      </div>
      {item.test_name && (
        <p className="text-slate-400 text-xs mt-0.5">📝 {item.test_name}</p>
      )}
      <p className="text-slate-400 text-xs mt-1 truncate">{item.root_cause}</p>
    </button>
  );
}

// ── Main App ──
function App() {
  const [errorLog, setErrorLog]   = useState('');
  const [testName, setTestName]   = useState('');
  const [result, setResult]       = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError]         = useState('');
  const [history, setHistory]     = useState([]);
  const [showHistory, setShowHistory] = useState(false);

  // Load history from localStorage on first render
  useEffect(() => {
    const saved = localStorage.getItem('fw-history');
    if (saved) setHistory(JSON.parse(saved));
  }, []); // [] = run only once on mount

  // Save history to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('fw-history', JSON.stringify(history));
  }, [history]); // run whenever history changes

  async function handleAnalyze() {
    if (!errorLog.trim()) {
      setError('Please paste a Playwright error log first!');
      return;
    }
    setIsLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await axios.post('http://localhost:8000/analyze', {
        error_log: errorLog,
        test_name: testName
      });

      const data = response.data;
      setResult(data);

      // Add to history (keep last 5 only)
      const historyItem = {
        ...data,
        timestamp: new Date().toLocaleTimeString(),
        errorLog: errorLog
      };
      setHistory(prev => [historyItem, ...prev].slice(0, 5));

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        'Could not connect. Is FastAPI running?'
      );
    } finally {
      setIsLoading(false);
    }
  }

  function handleHistorySelect(item) {
    setResult(item);
    setErrorLog(item.errorLog);
    setTestName(item.test_name || '');
    setShowHistory(false);
  }

  function handleClear() {
    setErrorLog('');
    setTestName('');
    setResult(null);
    setError('');
  }

  return (
    <div className="min-h-screen bg-slate-900 text-white p-6">
      <div className="max-w-2xl mx-auto">

        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-green-400 mb-2">🎭 FailWhisperer</h1>
          <p className="text-slate-400 text-sm">AI-Powered Playwright Test Failure Analyst</p>
        </div>

        {/* Test Name Input */}
        <div className="mb-3">
          <label className="block text-slate-300 text-sm font-semibold mb-1">
            Test Name <span className="text-slate-500 font-normal">(optional)</span>
          </label>
          <input
            type="text"
            value={testName}
            onChange={(e) => setTestName(e.target.value)}
            placeholder="e.g. Login Test, Checkout Flow..."
            className="w-full bg-slate-800 border border-slate-600 rounded-xl px-4 py-2 text-white text-sm placeholder:text-slate-500 focus:outline-none focus:border-green-500"
          />
        </div>

        {/* Error Log Textarea */}
        <div className="mb-3">
          <label className="block text-slate-300 text-sm font-semibold mb-1">
            Paste your Playwright error log:
          </label>
          <textarea
            value={errorLog}
            onChange={(e) => setErrorLog(e.target.value)}
            placeholder="TimeoutError: locator.click: Timeout 30000ms exceeded..."
            rows={7}
            className="w-full bg-slate-800 border border-slate-600 rounded-xl p-4 text-green-300 font-mono text-sm placeholder:text-slate-500 focus:outline-none focus:border-green-500 resize-none"
          />
        </div>

        {/* Buttons Row */}
        <div className="flex gap-3">
          <button
            onClick={handleAnalyze}
            disabled={isLoading}
            className="flex-1 bg-green-500 hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold py-3 rounded-xl transition-colors"
          >
            {isLoading ? '⏳ Analyzing...' : '🔍 Analyze Failure'}
          </button>

          <button
            onClick={() => setShowHistory(!showHistory)}
            className="px-4 py-3 bg-slate-700 hover:bg-slate-600 rounded-xl text-sm font-semibold transition-colors relative"
          >
            🕐 History
            {history.length > 0 && (
              <span className="absolute -top-1 -right-1 bg-green-500 text-white text-xs w-4 h-4 rounded-full flex items-center justify-center">
                {history.length}
              </span>
            )}
          </button>

          {(errorLog || result) && (
            <button
              onClick={handleClear}
              className="px-4 py-3 bg-slate-700 hover:bg-slate-600 rounded-xl text-sm font-semibold transition-colors"
            >
              🗑️ Clear
            </button>
          )}
        </div>

        {/* History Panel */}
        {showHistory && (
          <div className="mt-4 bg-slate-800 border border-slate-600 rounded-xl p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-bold text-slate-300">Recent Analyses</h3>
              {history.length > 0 && (
                <button
                  onClick={() => { setHistory([]); setShowHistory(false); }}
                  className="text-xs text-red-400 hover:text-red-300"
                >
                  Clear All
                </button>
              )}
            </div>
            {history.length === 0 ? (
              <p className="text-slate-500 text-sm text-center py-4">No history yet</p>
            ) : (
              <div className="space-y-2">
                {history.map((item, i) => (
                  <HistoryItem key={i} item={item} onSelect={handleHistorySelect} />
                ))}
              </div>
            )}
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="mt-4 bg-red-900/50 border border-red-500 rounded-xl p-4 text-red-300 text-sm">
            ❌ {error}
          </div>
        )}

        {/* Loading Skeleton */}
        {isLoading && <LoadingSkeleton />}

        {/* Result */}
        {!isLoading && result && <ResultCard result={result} />}

      </div>
    </div>
  );
}

export default App;