import React from 'react';
import Plot from 'react-plotly.js';

interface LineChartProps {
  dates: string[];
  series: {
    name: string;
    values: number[];
    color?: string;
  }[];
  title?: string;
  yAxisTitle?: string;
  showRangeSelector?: boolean;
}

export const LineChart: React.FC<LineChartProps> = ({
  dates,
  series,
  title,
  yAxisTitle,
  showRangeSelector = false,
}) => {
  const traces = series.map((s) => ({
    type: 'scatter' as const,
    mode: 'lines' as const,
    name: s.name,
    x: dates,
    y: s.values,
    line: s.color ? { color: s.color } : undefined,
  }));

  return (
    <Plot
      data={traces}
      layout={{
        autosize: true,
        title: title ? { text: title, font: { size: 16 } } : undefined,
        xaxis: {
          title: 'Date',
          type: 'date',
          ...(showRangeSelector
            ? {
                rangeselector: {
                  buttons: [
                    { count: 1, label: '1m', step: 'month', stepmode: 'backward' },
                    { count: 3, label: '3m', step: 'month', stepmode: 'backward' },
                    { count: 6, label: '6m', step: 'month', stepmode: 'backward' },
                    { step: 'all' },
                  ],
                },
                rangeslider: { visible: true },
              }
            : {}),
        },
        yaxis: {
          title: yAxisTitle,
        },
        margin: { t: title ? 50 : 20, b: showRangeSelector ? 100 : 60, l: 60, r: 20 },
        legend: {
          orientation: 'h',
          y: 1.1,
        },
        hovermode: 'x unified',
      }}
      useResizeHandler
      style={{ width: '100%', height: showRangeSelector ? '500px' : '400px' }}
      config={{ responsive: true }}
    />
  );
};
