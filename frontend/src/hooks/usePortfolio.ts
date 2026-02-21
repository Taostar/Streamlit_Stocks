import { useQuery } from '@tanstack/react-query';
import { portfolioApi } from '../api/portfolio';

// Cache times matching backend TTLs
const CACHE_5_MIN = 5 * 60 * 1000;
const CACHE_1_HOUR = 60 * 60 * 1000;
const CACHE_1_DAY = 24 * 60 * 60 * 1000;

export const usePortfolioOverview = () => {
  return useQuery({
    queryKey: ['portfolio', 'overview'],
    queryFn: portfolioApi.getOverview,
    staleTime: CACHE_5_MIN,
    refetchInterval: CACHE_5_MIN,
  });
};

export const useAllocation = () => {
  return useQuery({
    queryKey: ['portfolio', 'allocation'],
    queryFn: portfolioApi.getAllocation,
    staleTime: CACHE_5_MIN,
    refetchInterval: CACHE_5_MIN,
  });
};

export const useHoldings = () => {
  return useQuery({
    queryKey: ['holdings'],
    queryFn: portfolioApi.getHoldings,
    staleTime: CACHE_1_HOUR,
  });
};

export const useTopHoldings = (n: number) => {
  return useQuery({
    queryKey: ['holdings', 'top', n],
    queryFn: () => portfolioApi.getTopHoldings(n),
    staleTime: CACHE_1_HOUR,
  });
};

export const useCorrelationMatrix = () => {
  return useQuery({
    queryKey: ['correlation', 'matrix'],
    queryFn: portfolioApi.getCorrelationMatrix,
    staleTime: CACHE_1_HOUR,
  });
};

export const useExchangeRatePairs = () => {
  return useQuery({
    queryKey: ['exchange-rates', 'pairs'],
    queryFn: portfolioApi.getExchangeRatePairs,
    staleTime: CACHE_1_DAY,
  });
};

export const useExchangeRate = (pair: string) => {
  return useQuery({
    queryKey: ['exchange-rates', pair],
    queryFn: () => portfolioApi.getExchangeRate(pair),
    staleTime: CACHE_1_DAY,
    enabled: !!pair,
  });
};

export const useBenchmarkComparison = () => {
  return useQuery({
    queryKey: ['benchmark', 'comparison'],
    queryFn: portfolioApi.getBenchmarkComparison,
    staleTime: CACHE_1_DAY,
  });
};

export const useAvailableSymbols = () => {
  return useQuery({
    queryKey: ['performance', 'symbols'],
    queryFn: portfolioApi.getAvailableSymbols,
    staleTime: CACHE_1_HOUR,
  });
};

export const useSymbolPerformance = (symbol: string) => {
  return useQuery({
    queryKey: ['performance', symbol],
    queryFn: () => portfolioApi.getSymbolPerformance(symbol),
    staleTime: CACHE_1_HOUR,
    enabled: !!symbol,
  });
};
