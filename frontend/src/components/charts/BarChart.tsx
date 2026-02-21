import React from 'react';
import Plot from 'react-plotly.js';
import type { HoldingItem } from '../../types/portfolio';

interface BarChartProps {
  data: HoldingItem[];
  title?: string;
}

export const BarChart: React.FC<BarChartProps> = ({ data, title }) => {
  return (
    <Plot
      data={[
        {
          type: 'bar',
          x: data.map((d) => d.symbol),
          y: data.map((d) => d.market_value_cad),
          marker: {
            color: data.map((_, i) => `hsl(${(i * 360) / data.length}, 70%, 50%)`),
          },
          hovertemplate: '%{x}<br>Value: $%{y:,.2f}<extra></extra>',
        },
      ]}
      layout={{
        autosize: true,
        title: title ? { text: title, font: { size: 16 } } : undefined,
        xaxis: { title: 'Symbol' },
        yaxis: { title: 'Market Value (CAD)' },
        margin: { t: title ? 50 : 20, b: 60, l: 80, r: 20 },
      }}
      useResizeHandler
      style={{ width: '100%', height: '400px' }}
      config={{ responsive: true }}
    />
  );
};
