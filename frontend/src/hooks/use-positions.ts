import { useQuery } from '@tanstack/react-query';
import { getUnifiedPositions, Position, BrokerError } from '@/lib/api';

/**
 * Custom React Query hook resolving the Smart Hyper Broker endpoints.
 * Includes a polling interval mapping natively to support 60-second live updates automatically.
 */
export function usePositions() {
  return useQuery<{ data: Position[]; errors: BrokerError[] }, Error>({
    queryKey: ['positions'],
    queryFn: getUnifiedPositions,
    // Automatically refetch every 60 seconds ensuring UI stays natively synced while backend TTL prevents rate limit overflows
    refetchInterval: 60000, 
    staleTime: 55000, 
    retry: 3,
  });
}
