import { divIcon } from "leaflet";
import { useEffect } from "react";
import {
  MapContainer,
  Marker,
  Polyline,
  Popup,
  TileLayer,
  useMap,
} from "react-leaflet";

import { useIncidents } from "../hooks/useIncidents";
import { useResources } from "../hooks/useResources";
import { useCityStore } from "../store/cityStore";
import type { IncidentDetail, ResourceOut } from "../types";

const DELHI_CENTER: [number, number] = [28.6139, 77.209];

function markerClass(type: ResourceOut["type"]) {
  return `resource-marker resource-marker-${type}`;
}

function markerLabel(type: ResourceOut["type"]) {
  if (type === "ambulance") {
    return "AMB";
  }
  if (type === "hospital") {
    return "H";
  }
  return "POL";
}

function resourceIcon(resource: ResourceOut) {
  return divIcon({
    className: markerClass(resource.type),
    html: `<span>${markerLabel(resource.type)}</span>`,
    iconSize: [34, 34],
    iconAnchor: [17, 17],
    popupAnchor: [0, -18],
  });
}

const INCIDENT_COLORS = ["#ef4444", "#f59e0b", "#10b981", "#3b82f6", "#a855f7"];

function incidentColor(id: string) {
  let hash = 0;
  for (let i = 0; i < id.length; i += 1) {
    hash = (hash + id.charCodeAt(i)) % INCIDENT_COLORS.length;
  }
  return INCIDENT_COLORS[hash];
}
function incidentIcon(active: boolean, color: string) {
  return divIcon({
    className: active ? "incident-marker incident-marker-active" : "incident-marker",
    html: `<span style="background:${color}">INC</span>`,
    iconSize: active ? [42, 42] : [34, 34],
    iconAnchor: active ? [21, 21] : [17, 17],
    popupAnchor: [0, -20],
  });
}

function ActiveIncidentFocus({
  incidents,
  activeIncidentId,
}: {
  incidents: IncidentDetail[];
  activeIncidentId: string | null;
}) {
  const map = useMap();

  useEffect(() => {
    if (!activeIncidentId) {
      return;
    }
    const incident = incidents.find((item) => item.id === activeIncidentId);
    if (incident?.lat == null || incident.lng == null) {
      return;
    }
    map.flyTo([incident.lat, incident.lng], Math.max(map.getZoom(), 13), {
      duration: 0.6,
    });
  }, [activeIncidentId, incidents, map]);

  return null;
}

export function Map() {
  const { data: resources = [], isLoading, isError } = useResources();
  const { data: incidents = [] } = useIncidents();
  const activeIncidentId = useCityStore((state) => state.activeIncidentId);
  const setActiveIncident = useCityStore((state) => state.setActiveIncident);
  const resourcesById = new globalThis.Map(
    resources.map((resource) => [resource.id, resource]),
  );

  return (
    <div className="relative h-full bg-black">
      <MapContainer
        center={DELHI_CENTER}
        className="h-full w-full"
        scrollWheelZoom
        zoom={11}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <ActiveIncidentFocus
          activeIncidentId={activeIncidentId}
          incidents={incidents}
        />
        {resources.map((resource) => (
          <Marker
            icon={resourceIcon(resource)}
            key={resource.id}
            position={[resource.lat, resource.lng]}
          >
            <Popup>
              <div className="space-y-1">
                <p className="font-semibold">{resource.name}</p>
                <p>Type: {resource.type}</p>
                <p>Status: {resource.status}</p>
                <p>
                  Capacity: {resource.capacity_used}/{resource.capacity_total}
                </p>
              </div>
            </Popup>
          </Marker>
        ))}

        {incidents.map((incident) => {
          if (incident.lat == null || incident.lng == null) {
            return null;
          }
          const active = incident.id === activeIncidentId;
          const color = incidentColor(incident.id);
          return (
            <Marker
              icon={incidentIcon(active, color)}
              key={incident.id}
              position={[incident.lat, incident.lng]}
              eventHandlers={{
                click: () => setActiveIncident(incident.id),
              }}
            >
              <Popup>
                <div className="space-y-1">
                  <p className="font-semibold">{incident.severity}</p>
                  <p>{incident.description}</p>
                  <p>Status: {incident.status}</p>
                </div>
              </Popup>
            </Marker>
          );
        })}

        {incidents.flatMap((incident) => {
          if (incident.lat == null || incident.lng == null) {
            return [];
          }

          return incident.assignments.flatMap((assignment) => {
            const resource = resourcesById.get(assignment.resource_id);
            if (!resource) {
              return [];
            }

            const active = incident.id === activeIncidentId;
            const color = incidentColor(incident.id);
            return (
              <Polyline
                color={color}
                key={`${incident.id}-${assignment.id}`}
                opacity={active ? 0.95 : 0.45}
                pathOptions={{ dashArray: active ? undefined : "6 8" }}
                positions={[
                  [incident.lat!, incident.lng!],
                  [resource.lat, resource.lng],
                ]}
                weight={active ? 4 : 2}
              />
            );
          });
        })}
      </MapContainer>

      {(isLoading || isError) && (
        <div className="absolute left-4 top-4 z-[1000] border border-[var(--color-border)] bg-[var(--color-panel)] px-3 py-2 text-sm text-[var(--color-text)] shadow-lg">
          {isLoading
            ? "Loading Delhi resources..."
            : "Resources unavailable until the database is migrated and seeded."}
        </div>
      )}
    </div>
  );
}
