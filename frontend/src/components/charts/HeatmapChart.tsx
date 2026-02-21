import React from 'react';
import Plot from 'react-plotly.js';
import { CORRELATION_COLORSCALE } from '../../utils/colorUtils';
import type { CorrelationMatrix } from '../../types/portfolio';

interface HeatmapChartProps {
  data: CorrelationMatrix;
}

export const HeatmapChart: React.FC<HeatmapChartProps> = ({ data }) => {
  // Format annotations for each cell (lower triangle only)
  const annotations = [];
  for (let i = 0; i < data.symbols.length; i++) {
    for (let j = 0; j < data.symbols.length; j++) {
      const value = data.values[i][j];
      if (value !== null) {
        annotations.push({
          x: data.symbols[j],
          y: data.symbols[i],
          text: value.toFixed(2),
          font: { size: 10, color: Math.abs(value) > 0.5 ? 'white' : 'black' },
          showarrow: false,
        });
      }
    }
  }

  return (
    <Plot
      data={[
        {
          type: 'heatmap',
          x: data.symbols,
          y: data.symbols,
          z: data.values,
          colorscale: CORRELATION_COLORSCALE,
          zmin: -1,
          zmax: 1,
          hoverongaps: false,
          hovertemplate: '%{x} vs %{y}<br>Correlation: %{z:.2f}<extra></extra>',
          colorbar: {
            title: 'Correlation',
            titleside: 'right',
          },
        },
      ]}
      layout={{
        autosize: true,
        title: { text: 'Asset Correlation Heatmap', font: { size: 16 } },
        xaxis: {
          tickangle: 45,
          side: 'bottom',
        },
        yaxis: {
          autorange: 'reversed',
        },
        margin: { t: 50, b: 100, l: 100, r: 80 },
        annotations,
      }}
      useResizeHandler
      style={{ width: '100%', height: '500px' }}
      config={{ responsive: true }}
    />
  );
};
