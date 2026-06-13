import { useQuery } from "@tanstack/react-query";

import { getIncidents } from "../lib/api";
import { useCityStore } from "../store/cityStore";

export function useIncidents() {
  const setIncidents = useCityStore((state) => state.setIncidents);

  return useQuery({
    queryKey: ["incidents"],
    queryFn: async () => {
      const incidents = await getIncidents();
      setIncidents(incidents);
      return incidents;
    },
    refetchInterval: 2_000,
  });
}
