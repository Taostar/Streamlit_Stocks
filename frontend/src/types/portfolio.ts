export interface PortfolioOverview {
  total_value_cad: number;
  cumulative_return: number;
  avg_daily_return: number;
  sharpe_ratio: number;
  weighted_correlation: number | null;
  prev_day_change: number | null;
}

export interface AllocationItem {
  symbol: string;
  market_value_cad: number;
  percentage: number;
  currency: string;
  current_price: number;
}

export interface AllocationResponse {
  items: AllocationItem[];
  total_value_cad: number;
}

export interface HoldingItem {
  symbol: string;
  currency: string;
  quantity: number;
  current_price: number;
  market_value: number;
  market_value_cad: number;
  portfolio_pct: number;
  change_1d: number | null;
  change_1w: number | null;
  change_1m: number | null;
  change_6m: number | null;
  change_1y: number | null;
}

export interface HoldingsResponse {
  holdings: HoldingItem[];
  prev_day_change_pct: number | null;
}

export interface CorrelationMatrix {
  symbols: string[];
  values: (number | null)[][];
  weighted_correlation: number;
}

export interface ExchangeRateData {
  pair: string;
  dates: string[];
  close_prices: number[];
  current_rate: number;
  daily_change_pct: number;
  ytd_change_pct: number;
}

export interface BenchmarkData {
  dates: string[];
  portfolio: number[];
  qqq: number[];
  voo: number[];
}

export interface CandlestickData {
  symbol: string;
  dates: string[];
  open: number[];
  high: number[];
  low: number[];
  close: number[];
  volume: number[];
}
