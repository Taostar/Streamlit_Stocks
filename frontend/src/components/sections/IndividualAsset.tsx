import React, { useState, useEffect } from 'react';
import { useAvailableSymbols, useSymbolPerformance } from '../../hooks/usePortfolio';
import { CandlestickChart } from '../charts/CandlestickChart';

export const IndividualAsset: React.FC = () => {
  const { data: symbols, isLoading: symbolsLoading } = useAvailableSymbols();
  const [selectedSymbol, setSelectedSymbol] = useState('');
  const { data, isLoading, error } = useSymbolPerformance(selectedSymbol);

  useEffect(() => {
    if (symbols && symbols.length > 0 && !selectedSymbol) {
      setSelectedSymbol(symbols[0]);
    }
  }, [symbols, selectedSymbol]);

  if (symbolsLoading) {
    return <div className="text-center py-8">Loading symbols...</div>;
  }

  return (
    <section className="mb-8 bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold mb-2">Individual Asset Performance</h2>
      <p className="text-gray-600 mb-4">
        This section shows the past year's performance for each of your holdings.
      </p>

      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Select Asset to View:
        </label>
        <select
          value={selectedSymbol}
          onChange={(e) => setSelectedSymbol(e.target.value)}
          className="block w-full max-w-xs px-3 py-2 border border-gray-300 rounded-lg bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          {symbols?.map((symbol) => (
            <option key={symbol} value={symbol}>
              {symbol}
            </option>
          ))}
        </select>
      </div>

      {isLoading && (
        <div className="text-center py-8">Loading performance data...</div>
      )}

      {error && (
        <div className="text-center py-8 text-red-500">
          Failed to load performance data for {selectedSymbol}
        </div>
      )}

      {data && <CandlestickChart data={data} />}
    </section>
  );
};
