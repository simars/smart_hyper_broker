import { useQuery } from "@tanstack/react-query";
import { getInsight, InsightReport } from "@/lib/api";

export function useManagerThesis() {
  return useQuery<InsightReport, Error>({
    queryKey: ["insights", "manager-thesis"],
    queryFn: () => getInsight("manager-thesis"),
    staleTime: 5 * 60 * 1000,   // treat as fresh for 5 minutes (positions are TTL-cached anyway)
    retry: 1,
  });
}

export function useBehavioralBias() {
  return useQuery<InsightReport, Error>({
    queryKey: ["insights", "behavioral-bias"],
    queryFn: () => getInsight("behavioral-bias"),
    staleTime: 5 * 60 * 1000,
    retry: 1,
  });
}
