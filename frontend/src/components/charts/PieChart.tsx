import React from 'react';
import Plot from 'react-plotly.js';
import type { AllocationItem } from '../../types/portfolio';

interface PieChartProps {
  data: AllocationItem[];
}

export const PieChart: React.FC<PieChartProps> = ({ data }) => {
  return (
    <Plot
      data={[
        {
          type: 'pie',
          values: data.map((d) => d.market_value_cad),
          labels: data.map((d) => d.symbol),
          textinfo: 'percent+label',
          textposition: 'inside',
          hoverinfo: 'label+value+percent',
          customdata: data.map((d) => [
            d.percentage.toFixed(2),
            d.currency,
            d.current_price.toFixed(2),
          ]),
          hovertemplate:
            '%{label}<br>Value: $%{value:,.2f}<br>Currency: %{customdata[1]}<br>Price: $%{customdata[2]}<extra></extra>',
        },
      ]}
      layout={{
        autosize: true,
        showlegend: true,
        margin: { t: 20, b: 20, l: 20, r: 20 },
        legend: {
          orientation: 'h',
          y: -0.1,
        },
      }}
      useResizeHandler
      style={{ width: '100%', height: '400px' }}
      config={{ responsive: true }}
    />
  );
};
