import React from 'react';
import { useBenchmarkComparison } from '../../hooks/usePortfolio';
import { LineChart } from '../charts/LineChart';

export const BenchmarkComparison: React.FC = () => {
  const { data, isLoading, error } = useBenchmarkComparison();

  if (isLoading) {
    return <div className="text-center py-8">Loading benchmark data...</div>;
  }

  if (error || !data) {
    return (
      <div className="text-center py-8 text-red-500">
        Failed to load benchmark comparison data
      </div>
    );
  }

  return (
    <section className="mb-8 bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold mb-2">Market Benchmark Comparison</h2>
      <p className="text-gray-600 mb-4">
        This section shows the performance of Portfolio vs QQQ/VOO over the past
        year.
      </p>
      <LineChart
        dates={data.dates}
        series={[
          { name: 'Portfolio', values: data.portfolio, color: '#2563eb' },
          { name: 'QQQ', values: data.qqq, color: '#16a34a' },
          { name: 'VOO', values: data.voo, color: '#dc2626' },
        ]}
        title="Portfolio vs QQQ/VOO Performance (Normalized to 100)"
        yAxisTitle="Normalized Price (Start = 100)"
      />
    </section>
  );
};
