import { apiClient } from './client';
import type {
  PortfolioOverview,
  AllocationResponse,
  HoldingsResponse,
  CorrelationMatrix,
  ExchangeRateData,
  BenchmarkData,
  CandlestickData,
} from '../types/portfolio';

export const portfolioApi = {
  getOverview: async (): Promise<PortfolioOverview> => {
    const response = await apiClient.get<PortfolioOverview>('/portfolio/overview');
    return response.data;
  },

  getAllocation: async (): Promise<AllocationResponse> => {
    const response = await apiClient.get<AllocationResponse>('/portfolio/allocation');
    return response.data;
  },

  getHoldings: async (): Promise<HoldingsResponse> => {
    const response = await apiClient.get<HoldingsResponse>('/holdings');
    return response.data;
  },

  getTopHoldings: async (n: number): Promise<HoldingsResponse> => {
    const response = await apiClient.get<HoldingsResponse>(`/holdings/top/${n}`);
    return response.data;
  },

  getCorrelationMatrix: async (): Promise<CorrelationMatrix> => {
    const response = await apiClient.get<CorrelationMatrix>('/correlation/matrix');
    return response.data;
  },

  getExchangeRatePairs: async (): Promise<string[]> => {
    const response = await apiClient.get<string[]>('/exchange-rates');
    return response.data;
  },

  getExchangeRate: async (pair: string): Promise<ExchangeRateData> => {
    const response = await apiClient.get<ExchangeRateData>(`/exchange-rates/${encodeURIComponent(pair)}`);
    return response.data;
  },

  getBenchmarkComparison: async (): Promise<BenchmarkData> => {
    const response = await apiClient.get<BenchmarkData>('/benchmark/comparison');
    return response.data;
  },

  getAvailableSymbols: async (): Promise<string[]> => {
    const response = await apiClient.get<string[]>('/performance/symbols');
    return response.data;
  },

  getSymbolPerformance: async (symbol: string): Promise<CandlestickData> => {
    const response = await apiClient.get<CandlestickData>(`/performance/${symbol}`);
    return response.data;
  },
};
