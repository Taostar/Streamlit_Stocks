import React, { useState } from 'react';
import { useTopHoldings } from '../../hooks/usePortfolio';
import { BarChart } from '../charts/BarChart';

export const HoldingsBarChart: React.FC = () => {
  const [topN, setTopN] = useState(15);
  const { data, isLoading, error } = useTopHoldings(topN);

  if (isLoading) {
    return <div className="text-center py-8">Loading holdings data...</div>;
  }

  if (error || !data) {
    return (
      <div className="text-center py-8 text-red-500">
        Failed to load holdings data
      </div>
    );
  }

  return (
    <section className="mb-8 bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold mb-4">Holdings by Market Value (CAD)</h2>
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Number of top holdings to display: {topN}
        </label>
        <input
          type="range"
          min="5"
          max="30"
          value={topN}
          onChange={(e) => setTopN(parseInt(e.target.value))}
          className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
        />
      </div>
      <BarChart
        data={data.holdings}
        title={`Top ${topN} Holdings by Market Value (CAD)`}
      />
    </section>
  );
};
