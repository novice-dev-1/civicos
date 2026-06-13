import { Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft } from "lucide-react";
import {
  Bar,
  BarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { getKPI, getKpiComparison, getResourcesLoad } from "../lib/api";

export function KPIDashboard() {
  const { data: kpi } = useQuery({ queryKey: ["kpi"], queryFn: getKPI, refetchInterval: 5000 });
  const { data: comparison } = useQuery({
    queryKey: ["kpi-comparison"],
    queryFn: getKpiComparison,
    refetchInterval: 10000,
  });
  const { data: hospitalLoad = [] } = useQuery({
    queryKey: ["hospital-load"],
    queryFn: getResourcesLoad,
    refetchInterval: 5000,
  });

  const avgTtc = kpi?.avg_time_to_care_min ?? kpi?.avg_time_to_care;

  return (
    <main className="min-h-screen bg-[var(--color-bg)] px-6 py-5 text-[var(--color-text)]">
      <Link
        className="inline-flex h-9 items-center gap-2 border border-[var(--color-border)] px-3 text-sm transition hover:border-[var(--color-accent)]"
        to="/"
      >
        <ArrowLeft className="size-4" aria-hidden="true" />
        Dashboard
      </Link>
      <section className="mt-6">
        <p className="text-sm uppercase tracking-[0.18em] text-[var(--color-muted)]">
          KPI Dashboard
        </p>
        <h1 className="mt-2 text-3xl font-semibold">Operational Metrics</h1>
      </section>

      <div className="mt-8 grid gap-4 sm:grid-cols-3">
        <div className="border border-[var(--color-border)] bg-[var(--color-panel)] p-4">
          <p className="text-xs text-[var(--color-muted)]">Avg Time-to-Care</p>
          <p className="mt-2 text-3xl font-semibold">
            {avgTtc ? `${avgTtc} min` : "—"}
          </p>
        </div>
        <div className="border border-[var(--color-border)] bg-[var(--color-panel)] p-4">
          <p className="text-xs text-[var(--color-muted)]">Resource Utilization</p>
          <p className="mt-2 text-3xl font-semibold">
            {kpi?.resource_utilization
              ? `${Math.round(kpi.resource_utilization * 100)}%`
              : "—"}
          </p>
        </div>
        <div className="border border-[var(--color-border)] bg-[var(--color-panel)] p-4">
          <p className="text-xs text-[var(--color-muted)]">Hospital Load Variance</p>
          <p className="mt-2 text-3xl font-semibold">
            {kpi?.hospital_load_variance || "—"}
          </p>
        </div>
      </div>

      {comparison && (
        <section className="mt-8 border border-[var(--color-border)] bg-[var(--color-panel)] p-4">
          <h2 className="text-lg font-semibold">CivicOS vs Naive Baseline</h2>
          <div className="mt-4 flex gap-8">
            <div>
              <p className="text-xs text-[var(--color-muted)]">CivicOS</p>
              <p className="text-2xl font-semibold text-green-400">
                {comparison.civicos.avg_time_to_care || "—"} min
              </p>
            </div>
            <div>
              <p className="text-xs text-[var(--color-muted)]">Naive</p>
              <p className="text-2xl font-semibold text-orange-400">
                {comparison.naive.avg_time_to_care || "—"} min
              </p>
            </div>
            {comparison.improvement_pct > 0 && (
              <div>
                <p className="text-xs text-[var(--color-muted)]">Improvement</p>
                <p className="text-2xl font-semibold">{comparison.improvement_pct}%</p>
              </div>
            )}
          </div>
        </section>
      )}

      <section className="mt-8 border border-[var(--color-border)] bg-[var(--color-panel)] p-4">
        <h2 className="mb-4 text-lg font-semibold">Hospital ICU Load</h2>
        <div className="h-64">
          <ResponsiveContainer height="100%" width="100%">
            <BarChart data={hospitalLoad}>
              <XAxis dataKey="name" hide />
              <YAxis domain={[0, 1]} />
              <Tooltip />
              <Bar dataKey="ratio" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>
    </main>
  );
}
