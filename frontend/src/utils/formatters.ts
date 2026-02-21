/**
 * Format number as currency
 */
export const formatCurrency = (value: number, decimals = 2): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'CAD',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
};

/**
 * Format number as percentage
 */
export const formatPercent = (value: number | null, decimals = 2): string => {
  if (value === null) return 'N/A';
  return `${(value * 100).toFixed(decimals)}%`;
};

/**
 * Format number with commas
 */
export const formatNumber = (value: number, decimals = 2): string => {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
};

/**
 * Format exchange rate
 */
export const formatExchangeRate = (value: number, isBTC = false): string => {
  if (isBTC) {
    return formatNumber(value, 2);
  }
  return value.toFixed(4);
};
