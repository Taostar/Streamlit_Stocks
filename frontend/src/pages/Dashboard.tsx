import React from 'react';
import { PortfolioOverview } from '../components/sections/PortfolioOverview';
import { AssetAllocation } from '../components/sections/AssetAllocation';
import { CurrentHoldings } from '../components/sections/CurrentHoldings';
import { HoldingsBarChart } from '../components/sections/HoldingsBarChart';
import { CorrelationMatrix } from '../components/sections/CorrelationMatrix';
import { ExchangeRates } from '../components/sections/ExchangeRates';
import { BenchmarkComparison } from '../components/sections/BenchmarkComparison';
import { IndividualAsset } from '../components/sections/IndividualAsset';

export const Dashboard: React.FC = () => {
  return (
    <div className="space-y-6">
      <PortfolioOverview />
      <AssetAllocation />
      <CurrentHoldings />
      <HoldingsBarChart />
      <CorrelationMatrix />
      <ExchangeRates />
      <BenchmarkComparison />
      <IndividualAsset />

      {/* Resources section */}
      <section className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">📚 Resources</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <a
            href="https://www.notion.so/Stock-Note-03acb655380c44f98dbce4117d698539"
            target="_blank"
            rel="noopener noreferrer"
            className="block p-4 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition-colors text-center"
          >
            <div className="font-medium">Stock Note</div>
            <div className="text-sm text-gray-300">Notion</div>
          </a>
          <a
            href="https://www.macrotrends.net/stocks/research"
            target="_blank"
            rel="noopener noreferrer"
            className="block p-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-center"
          >
            <div className="font-medium">Macrotrends</div>
            <div className="text-sm text-blue-200">Basic Analysis</div>
          </a>
          <a
            href="https://finance.yahoo.com/quote/IFC.TO/"
            target="_blank"
            rel="noopener noreferrer"
            className="block p-4 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors text-center"
          >
            <div className="font-medium">Yahoo Finance</div>
            <div className="text-sm text-purple-200">Advanced charting</div>
          </a>
        </div>
      </section>
    </div>
  );
};
