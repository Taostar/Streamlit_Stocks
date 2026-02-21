/**
 * Get color for return value based on intensity.
 * Matches the Streamlit color_change function from app.py:25-48
 */
export const getReturnColor = (value: number | null): string => {
  if (value === null || value === 0) return 'inherit';

  if (value > 0) {
    if (value > 0.1) return '#006400'; // Dark green
    if (value > 0.05) return '#008000'; // Green
    return '#90EE90'; // Light green
  } else {
    if (value < -0.1) return '#8B0000'; // Dark red
    if (value < -0.05) return '#FF0000'; // Red
    return '#FFA07A'; // Light red
  }
};

/**
 * Get Tailwind class for return value
 */
export const getReturnColorClass = (value: number | null): string => {
  if (value === null || value === 0) return '';

  if (value > 0) {
    if (value > 0.1) return 'text-green-800';
    if (value > 0.05) return 'text-green-600';
    return 'text-green-400';
  } else {
    if (value < -0.1) return 'text-red-800';
    if (value < -0.05) return 'text-red-600';
    return 'text-red-400';
  }
};

/**
 * Custom colorscale for correlation heatmap
 * Matches the Streamlit custom colormap from app.py:184-185
 */
export const CORRELATION_COLORSCALE: [number, string][] = [
  [0, '#053061'],     // Dark blue (-1)
  [0.25, '#2166ac'],  // Blue
  [0.4, '#92c5de'],   // Light blue
  [0.5, '#f7f7f7'],   // White (0)
  [0.6, '#f4a582'],   // Light red
  [0.75, '#d6604d'],  // Red
  [1, '#b2182b'],     // Dark red (+1)
];
