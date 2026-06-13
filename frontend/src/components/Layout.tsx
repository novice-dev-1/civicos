import { AgentFeed } from "./AgentFeed";
import { IncidentList } from "./IncidentList";
import { KPITicker } from "./KPITicker";
import { Map } from "./Map";
import { Timeline } from "./Timeline";

export function Layout() {
  return (
    <main className="h-screen overflow-hidden bg-[var(--color-bg)] text-[var(--color-text)]">
      <KPITicker />
      <section className="flex h-[calc(100vh-3rem-8rem)] min-h-0 border-b border-[var(--color-border)]">
        <aside className="w-72 shrink-0 overflow-y-auto border-r border-[var(--color-border)] bg-[var(--color-panel)]">
          <IncidentList />
        </aside>
        <section className="min-w-0 flex-1">
          <Map />
        </section>
        <aside className="w-80 shrink-0 overflow-y-auto border-l border-[var(--color-border)] bg-[var(--color-panel)]">
          <AgentFeed />
        </aside>
      </section>
      <Timeline />
    </main>
  );
}
