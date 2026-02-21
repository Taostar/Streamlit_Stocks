import React, { useState } from 'react';
import { useExchangeRate } from '../../hooks/usePortfolio';
import { LineChart } from '../charts/LineChart';
import { MetricCard } from '../common/MetricCard';
import { formatExchangeRate } from '../../utils/formatters';
import { getReturnColor } from '../../utils/colorUtils';

const CURRENCY_PAIRS = ['USD/CAD', 'CAD/CNY', 'USD/CNY', 'BTC/USD'];

export const ExchangeRates: React.FC = () => {
  const [selectedPair, setSelectedPair] = useState('USD/CAD');
  const { data, isLoading, error } = useExchangeRate(selectedPair);

  return (
    <section className="mb-8 bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold mb-2">Exchange Rate</h2>
      <p className="text-gray-600 mb-4">
        Track historical exchange rates between major currencies and Bitcoin.
      </p>

      <div className="flex gap-2 mb-4">
        {CURRENCY_PAIRS.map((pair) => (
          <button
            key={pair}
            onClick={() => setSelectedPair(pair)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              selectedPair === pair
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {pair}
          </button>
        ))}
      </div>

      {isLoading && (
        <div className="text-center py-8">Loading exchange rate data...</div>
      )}

      {error && (
        <div className="text-center py-8 text-red-500">
          Failed to load exchange rate data for {selectedPair}
        </div>
      )}

      {data && (
        <>
          <div className="grid grid-cols-3 gap-4 mb-4">
            <MetricCard
              label="Current Rate"
              value={formatExchangeRate(
                data.current_rate,
                selectedPair === 'BTC/USD'
              )}
              change={`${data.daily_change_pct >= 0 ? '+' : ''}${data.daily_change_pct.toFixed(2)}%`}
              changeColor={getReturnColor(data.daily_change_pct / 100)}
            />
            <MetricCard
              label="Year-to-Date Change"
              value={`${data.ytd_change_pct >= 0 ? '+' : ''}${data.ytd_change_pct.toFixed(2)}%`}
            />
          </div>

          <LineChart
            dates={data.dates}
            series={[
              {
                name: selectedPair,
                values: data.close_prices,
                color: '#2563eb',
              },
            ]}
            title={`${selectedPair} Exchange Rate (Past Year)`}
            yAxisTitle="Exchange Rate"
            showRangeSelector
          />
        </>
      )}
    </section>
  );
};
