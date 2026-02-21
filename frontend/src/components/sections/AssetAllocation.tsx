import React from 'react';
import { useAllocation } from '../../hooks/usePortfolio';
import { PieChart } from '../charts/PieChart';

export const AssetAllocation: React.FC = () => {
  const { data, isLoading, error } = useAllocation();

  if (isLoading) {
    return <div className="text-center py-8">Loading allocation data...</div>;
  }

  if (error || !data) {
    return (
      <div className="text-center py-8 text-red-500">
        Failed to load allocation data
      </div>
    );
  }

  return (
    <section className="mb-8 bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold mb-4">Asset Allocation (CAD Market Value)</h2>
      <PieChart data={data.items} />
    </section>
  );
};
