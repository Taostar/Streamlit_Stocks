import React, { useState } from 'react';
import { useCorrelationMatrix } from '../../hooks/usePortfolio';
import { HeatmapChart } from '../charts/HeatmapChart';

export const CorrelationMatrix: React.FC = () => {
  const { data, isLoading, error } = useCorrelationMatrix();
  const [showExplanation, setShowExplanation] = useState(false);

  if (isLoading) {
    return <div className="text-center py-8">Loading correlation matrix...</div>;
  }

  if (error || !data) {
    return (
      <div className="text-center py-8 text-red-500">
        Failed to load correlation data. Ensure your portfolio contains multiple
        assets with historical price data.
      </div>
    );
  }

  return (
    <section className="mb-8 bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold mb-2">Portfolio Correlation Matrix</h2>
      <p className="text-gray-600 mb-4">
        Visualize the correlation between assets in your portfolio.
      </p>
      <HeatmapChart data={data} />

      <button
        onClick={() => setShowExplanation(!showExplanation)}
        className="mt-4 text-blue-600 hover:text-blue-800 text-sm font-medium"
      >
        {showExplanation ? '▼ Hide explanation' : '▶ What does this correlation matrix show?'}
      </button>

      {showExplanation && (
        <div className="mt-4 p-4 bg-gray-50 rounded-lg text-sm text-gray-700">
          <p className="mb-2">
            This correlation matrix shows how the returns of different assets in
            your portfolio move in relation to each other:
          </p>
          <ul className="list-disc list-inside space-y-1">
            <li>
              <strong>+1.00</strong>: Perfect positive correlation - assets move
              exactly the same way
            </li>
            <li>
              <strong>0.00</strong>: No correlation - assets move independently
              of each other
            </li>
            <li>
              <strong>-1.00</strong>: Perfect negative correlation - assets move
              exactly opposite to each other
            </li>
          </ul>
          <p className="mt-2">
            A well-diversified portfolio typically includes assets with low or
            negative correlations to each other, which can help reduce overall
            portfolio risk.
          </p>
        </div>
      )}
    </section>
  );
};
