import { Activity, Ambulance, Clock3 } from "lucide-react";
import { useQuery } from "@tanstack/react-query";

import { getKPI } from "../lib/api";

function formatMetric(value: number | undefined, suffix: string) {
  if (value == null || value === 0) {
    return "—";
  }
  return `${value}${suffix}`;
}

function TickerItem({
  icon: Icon,
  label,
  value,
}: {
  icon: typeof Clock3;
  label: string;
  value: string;
}) {
  return (
    <div className="flex items-center gap-2 text-sm">
      <Icon className="size-4 text-[var(--color-accent)]" aria-hidden="true" />
      <span className="text-[var(--color-muted)]">{label}</span>
      <span className="font-semibold text-[var(--color-text)]">{value}</span>
    </div>
  );
}

export function KPITicker() {
  const { data: kpi } = useQuery({
    queryKey: ["kpi"],
    queryFn: getKPI,
    refetchInterval: 5000,
  });

  return (
    <header className="flex h-12 items-center justify-between border-b border-[var(--color-border)] bg-[var(--color-panel)] px-4">
      <div className="text-sm font-semibold tracking-[0.18em] text-[var(--color-accent)]">
        CIVICOS
      </div>
      <div className="flex items-center gap-6">
        <TickerItem
          icon={Clock3}
          label="Avg Time-to-Care"
          value={formatMetric(kpi?.avg_time_to_care_min ?? kpi?.avg_time_to_care, " min")}
        />
        <TickerItem
          icon={Ambulance}
          label="Utilization"
          value={
            kpi?.resource_utilization
              ? `${Math.round(kpi.resource_utilization * 100)}%`
              : "—"
          }
        />
        <TickerItem
          icon={Activity}
          label="Load Variance"
          value={formatMetric(kpi?.hospital_load_variance, "")}
        />
      </div>
    </header>
  );
}
