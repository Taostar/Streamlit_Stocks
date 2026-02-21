import React from 'react';
import Plot from 'react-plotly.js';
import type { CandlestickData } from '../../types/portfolio';

interface CandlestickChartProps {
  data: CandlestickData;
}

export const CandlestickChart: React.FC<CandlestickChartProps> = ({ data }) => {
  // Normalize volume for color scale
  const maxVolume = Math.max(...data.volume);
  const normalizedVolume = data.volume.map((v) => v / maxVolume);

  return (
    <Plot
      data={[
        {
          type: 'candlestick',
          x: data.dates,
          open: data.open,
          high: data.high,
          low: data.low,
          close: data.close,
          name: 'Price',
          increasing: { line: { color: '#26A69A' } },
          decreasing: { line: { color: '#EF5350' } },
        },
        {
          type: 'bar',
          x: data.dates,
          y: data.volume,
          name: 'Volume',
          yaxis: 'y2',
          marker: {
            color: normalizedVolume,
            colorscale: 'Plasma',
          },
          opacity: 0.6,
        },
      ]}
      layout={{
        autosize: true,
        title: { text: `${data.symbol} Price and Volume`, font: { size: 16 } },
        xaxis: {
          title: 'Date',
          type: 'date',
          rangebreaks: [
            { bounds: ['sat', 'mon'] }, // Hide weekends
          ],
        },
        yaxis: {
          title: 'Price',
          side: 'left',
        },
        yaxis2: {
          title: 'Volume',
          side: 'right',
          overlaying: 'y',
          showgrid: false,
          titlefont: { color: 'rgba(58, 71, 80, 0.6)' },
          tickfont: { color: 'rgba(58, 71, 80, 0.6)' },
        },
        margin: { t: 50, b: 60, l: 60, r: 60 },
        legend: {
          orientation: 'h',
          y: 1.12,
          x: 1,
          xanchor: 'right',
        },
        height: 600,
      }}
      useResizeHandler
      style={{ width: '100%', height: '600px' }}
      config={{ responsive: true }}
    />
  );
};
