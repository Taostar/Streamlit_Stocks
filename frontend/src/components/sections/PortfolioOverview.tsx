import React from 'react';
import { usePortfolioOverview } from '../../hooks/usePortfolio';
import { MetricCard } from '../common/MetricCard';
import { formatCurrency, formatPercent } from '../../utils/formatters';
import { getReturnColor } from '../../utils/colorUtils';

export const PortfolioOverview: React.FC = () => {
  const { data, isLoading, error } = usePortfolioOverview();

  if (isLoading) {
    return <div className="text-center py-8">Loading portfolio overview...</div>;
  }

  if (error || !data) {
    return (
      <div className="text-center py-8 text-red-500">
        Failed to load portfolio overview
      </div>
    );
  }

  return (
    <section className="mb-8">
      <h2 className="text-xl font-semibold mb-4">Portfolio Overview</h2>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <MetricCard
          label="Total Portfolio Value (CAD)"
          value={formatCurrency(data.total_value_cad)}
        />
        <MetricCard
          label="Cumulative Return"
          value={formatPercent(data.cumulative_return)}
        />
        <MetricCard
          label="Average Daily Return"
          value={formatPercent(data.avg_daily_return)}
        />
        <MetricCard
          label="Sharpe Ratio"
          value={data.sharpe_ratio.toFixed(2)}
        />
        <MetricCard
          label="Weighted Correlation"
          value={data.weighted_correlation?.toFixed(2) ?? 'N/A'}
        />
        <MetricCard
          label="Previous Day Change"
          value={formatPercent(data.prev_day_change)}
          changeColor={getReturnColor(data.prev_day_change)}
        />
      </div>
    </section>
  );
};
