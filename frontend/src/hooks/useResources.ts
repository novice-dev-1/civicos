import { useQuery } from "@tanstack/react-query";

import { getResources } from "../lib/api";

export function useResources() {
  return useQuery({
    queryKey: ["resources"],
    queryFn: getResources,
    refetchInterval: 30_000,
  });
}
