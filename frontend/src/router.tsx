import {
  createRootRoute,
  createRoute,
  createRouter,
  Outlet,
} from "@tanstack/react-router";

import { Layout } from "./components/Layout";
import { KPIDashboard } from "./components/KPIDashboard";
import { IncidentDetailPage } from "./routes/incident.$id";

const rootRoute = createRootRoute({
  component: () => <Outlet />,
});

const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/",
  component: Layout,
});

const kpiRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/kpi",
  component: KPIDashboard,
});

const incidentRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/incident/$id",
  component: IncidentDetailPage,
});

const routeTree = rootRoute.addChildren([indexRoute, kpiRoute, incidentRoute]);

export const router = createRouter({ routeTree });

declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}
