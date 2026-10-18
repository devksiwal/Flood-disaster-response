import React, { useEffect, useMemo } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polygon, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import { Incident, Team, FloodSensor, ReliefCamp, RescueRoute, FloodRiskZone } from '../types';
import { Shield, AlertCircle, Waves, Home, Navigation, Radio } from 'lucide-react';

interface LiveMapProps {
  incidents: Incident[];
  teams: Team[];
  sensors: FloodSensor[];
  camps: ReliefCamp[];
  routes: RescueRoute[];
  zones: FloodRiskZone[];
  selectedIncidentId?: string | null;
  onSelectIncident?: (id: string) => void;
}

// Center controller hook to zoom or focus on selected incident
function MapViewController({ selectedIncident, defaultCenter }: { selectedIncident?: Incident | null; defaultCenter: [number, number] }) {
  const map = useMap();
  useEffect(() => {
    if (selectedIncident) {
      map.flyTo([selectedIncident.latitude, selectedIncident.longitude], 14, { duration: 1.2 });
    }
  }, [selectedIncident, map]);

  return null;
}

export const LiveMap: React.FC<LiveMapProps> = ({
  incidents,
  teams,
  sensors,
  camps,
  routes,
  zones,
  selectedIncidentId,
  onSelectIncident
}) => {
  const defaultCenter: [number, number] = [26.155, 91.750];

  const selectedIncident = useMemo(() => {
    return incidents.find(i => i.id === selectedIncidentId) || null;
  }, [incidents, selectedIncidentId]);

  // Create custom Leaflet HTML DivIcons
  const createIncidentIcon = (priority: string, isSelected: boolean) => {
    const isCritical = priority === 'CRITICAL';
    const isHigh = priority === 'HIGH';
    const colorClass = isCritical ? 'bg-red-600 border-red-300' : isHigh ? 'bg-amber-600 border-amber-300' : 'bg-blue-600 border-blue-300';
    const ringClass = isCritical ? 'animate-pulse-ring' : '';

    return L.divIcon({
      className: 'custom-leaflet-icon',
      html: `
        <div class="relative flex items-center justify-center w-8 h-8 ${isSelected ? 'scale-125 z-50' : ''}">
          <div class="absolute w-full h-full rounded-full ${colorClass} opacity-60 ${ringClass}"></div>
          <div class="relative w-7 h-7 rounded-full ${colorClass} border-2 text-white flex items-center justify-center shadow-lg font-mono text-[10px] font-bold">
            !
          </div>
        </div>
      `,
      iconSize: [32, 32],
      iconAnchor: [16, 16]
    });
  };

  const createTeamIcon = (agency: string, status: string) => {
    const isDispatched = status === 'DISPATCHED';
    const colorClass = isDispatched ? 'bg-cyan-500 border-cyan-200' : 'bg-emerald-600 border-emerald-300';
    return L.divIcon({
      className: 'custom-leaflet-icon',
      html: `
        <div class="relative flex items-center justify-center w-7 h-7">
          <div class="w-6 h-6 rounded-md ${colorClass} border text-white flex items-center justify-center shadow-md font-mono text-[9px] font-extrabold tracking-tighter">
            ${agency === 'NDRF' ? 'ND' : agency === 'COAST_GUARD' ? 'CG' : agency === 'MEDICAL_CORPS' ? 'MD' : 'SD'}
          </div>
        </div>
      `,
      iconSize: [28, 28],
      iconAnchor: [14, 14]
    });
  };

  const createCampIcon = (beds: number) => {
    return L.divIcon({
      className: 'custom-leaflet-icon',
      html: `
        <div class="relative flex items-center justify-center w-7 h-7">
          <div class="w-6 h-6 rounded-md bg-indigo-600 border border-indigo-300 text-white flex items-center justify-center shadow-md font-mono text-[9px] font-bold">
            ⌂
          </div>
        </div>
      `,
      iconSize: [28, 28],
      iconAnchor: [14, 14]
    });
  };

  const createSensorIcon = (status: string) => {
    const color = status === 'CRITICAL' ? 'bg-red-500' : status === 'WARNING' ? 'bg-amber-500' : 'bg-emerald-500';
    return L.divIcon({
      className: 'custom-leaflet-icon',
      html: `
        <div class="relative flex items-center justify-center w-6 h-6">
          <div class="w-5 h-5 rounded-full ${color} border border-white text-white flex items-center justify-center shadow-sm text-[8px]">
            ≋
          </div>
        </div>
      `,
      iconSize: [24, 24],
      iconAnchor: [12, 12]
    });
  };

  return (
    <div className="relative w-full h-[450px] lg:h-[550px] rounded-xl overflow-hidden border border-slate-800 shadow-2xl bg-slate-950">
      {/* Tactical Map Overlay Header */}
      <div className="absolute top-3 left-3 z-[1000] bg-slate-900/90 backdrop-blur-md px-3 py-1.5 rounded-lg border border-slate-700/80 text-xs font-mono flex items-center gap-3">
        <div className="flex items-center gap-1.5 text-cyan-400 font-bold">
          <Navigation className="w-3.5 h-3.5" />
          <span>TACTICAL GEOSPATIAL RADAR</span>
        </div>
        <div className="h-3 w-px bg-slate-700"></div>
        <span className="text-slate-400">Layer: Composite Hydro-Risk & Fleet</span>
      </div>

      {/* Map Legend */}
      <div className="absolute bottom-4 left-4 z-[1000] bg-slate-900/90 backdrop-blur-md p-2.5 rounded-lg border border-slate-800 text-[11px] font-mono text-slate-300 flex flex-wrap gap-3">
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-red-600 animate-ping"></span>
          <span>Critical SOS</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span>
          <span>High Priority</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded bg-cyan-500"></span>
          <span>Rescue Unit</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded bg-indigo-600"></span>
          <span>Relief Camp</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
          <span>River Gauge</span>
        </div>
      </div>

      <MapContainer
        center={defaultCenter}
        zoom={13}
        scrollWheelZoom={true}
        className="w-full h-full"
      >
        {/* Dark High-Tech Base Tiles (CartoDB Dark Matter) */}
        <TileLayer
          attribution='&copy; <a href="https://carto.com/">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          maxZoom={19}
        />

        <MapViewController selectedIncident={selectedIncident} defaultCenter={defaultCenter} />

        {/* 1. Render Flood Risk Zones */}
        {zones.map((zone) => {
          const isExtreme = zone.risk_level === 'EXTREME';
          const isHigh = zone.risk_level === 'HIGH';
          const fillColor = isExtreme ? '#ef4444' : isHigh ? '#f59e0b' : '#3b82f6';
          return (
            <Polygon
              key={zone.id}
              positions={zone.polygon}
              pathOptions={{
                color: fillColor,
                weight: 1.5,
                fillColor: fillColor,
                fillOpacity: isExtreme ? 0.28 : 0.16,
                dashArray: isExtreme ? '4, 4' : undefined
              }}
            >
              <Popup>
                <div className="text-xs p-1">
                  <div className="font-bold text-red-400 uppercase text-[10px] tracking-wide mb-1">
                    Flood Inundation Zone
                  </div>
                  <h4 className="font-semibold text-slate-100">{zone.name}</h4>
                  <div className="mt-1 space-y-0.5 text-slate-300 font-mono text-[11px]">
                    <div>Risk: <span className="font-bold text-amber-400">{zone.risk_level}</span></div>
                    <div>Avg Water Depth: <span className="text-cyan-400">{zone.avg_depth_meters}m</span></div>
                    <div>Flow Current: <span className="text-slate-200">{zone.current_speed_knots} knots</span></div>
                    <div>Boat Navigable: <span className={zone.is_navigable_by_boat ? 'text-emerald-400' : 'text-red-400'}>{zone.is_navigable_by_boat ? 'YES' : 'NO'}</span></div>
                  </div>
                </div>
              </Popup>
            </Polygon>
          );
        })}

        {/* 2. Render Tactical Rescue Routes */}
        {routes.map((route) => (
          <Polyline
            key={route.id}
            positions={route.waypoints}
            pathOptions={{
              color: '#06b6d4',
              weight: 4,
              opacity: 0.85,
              dashArray: '6, 6'
            }}
          >
            <Popup>
              <div className="text-xs p-1">
                <span className="text-cyan-400 font-mono font-bold text-[10px]">ACTIVE RESCUE CORRIDOR</span>
                <p className="text-slate-200 mt-1 font-sans">{route.route_summary}</p>
                <div className="font-mono text-[11px] text-slate-400 mt-1">
                  Distance: <span className="text-white font-bold">{route.distance_km} km</span> | ETA: <span className="text-emerald-400 font-bold">{route.estimated_minutes} mins</span>
                </div>
              </div>
            </Popup>
          </Polyline>
        ))}

        {/* 3. Render Incidents */}
        {incidents.map((inc) => (
          <Marker
            key={inc.id}
            position={[inc.latitude, inc.longitude]}
            icon={createIncidentIcon(inc.priority_level, inc.id === selectedIncidentId)}
            eventHandlers={{
              click: () => onSelectIncident && onSelectIncident(inc.id)
            }}
          >
            <Popup>
              <div className="text-xs p-1 max-w-[220px]">
                <div className="flex items-center justify-between gap-2 mb-1">
                  <span className="font-mono text-[10px] text-cyan-400 font-bold">{inc.id}</span>
                  <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${
                    inc.priority_level === 'CRITICAL' ? 'bg-red-950 text-red-400 border border-red-800' : 'bg-amber-950 text-amber-400 border border-amber-800'
                  }`}>
                    {inc.priority_level} ({inc.priority_score})
                  </span>
                </div>
                <h4 className="font-bold text-slate-100 text-xs line-clamp-1">{inc.title}</h4>
                <p className="text-[11px] text-slate-300 italic mt-1 line-clamp-2">"{inc.raw_sos}"</p>
                <div className="mt-2 text-[11px] font-mono space-y-0.5 text-slate-400 border-t border-slate-800 pt-1">
                  <div>Victims: <span className="text-white font-bold">{inc.victim_count}</span> (Eld: {inc.elderly_count}, Chd: {inc.children_count})</div>
                  <div>Water Depth: <span className="text-cyan-400 font-bold">{inc.water_depth_meters}m</span></div>
                  <div>Status: <span className="text-emerald-400 font-bold">{inc.status}</span></div>
                  {inc.assigned_team_id && <div>Team: <span className="text-cyan-300 font-bold">{inc.assigned_team_id}</span></div>}
                </div>
              </div>
            </Popup>
          </Marker>
        ))}

        {/* 4. Render Rescue Teams */}
        {teams.map((team) => (
          <Marker
            key={team.id}
            position={[team.latitude, team.longitude]}
            icon={createTeamIcon(team.agency, team.status)}
          >
            <Popup>
              <div className="text-xs p-1">
                <span className="font-mono text-[10px] text-cyan-400 font-bold">{team.agency} RESCUE SQUAD</span>
                <h4 className="font-bold text-slate-100 text-xs mt-0.5">{team.callsign}</h4>
                <div className="mt-1.5 font-mono text-[11px] space-y-0.5 text-slate-300">
                  <div>Status: <span className="text-emerald-400 font-bold">{team.status}</span></div>
                  <div>Fleet: <span className="text-white font-bold">{team.boats_count} Boats, {team.amphibious_vehicles} Amphibious</span></div>
                  <div>Personnel: <span className="text-white font-bold">{team.personnel_count} Rescuers</span></div>
                  <div>VHF Channel: <span className="text-cyan-400">{team.contact_radio}</span></div>
                </div>
              </div>
            </Popup>
          </Marker>
        ))}

        {/* 5. Render Relief Camps */}
        {camps.map((camp) => (
          <Marker
            key={camp.id}
            position={[camp.latitude, camp.longitude]}
            icon={createCampIcon(camp.available_beds)}
          >
            <Popup>
              <div className="text-xs p-1">
                <span className="font-mono text-[10px] text-indigo-400 font-bold">DESIGNATED SAFE SHELTER</span>
                <h4 className="font-bold text-slate-100 text-xs mt-0.5">{camp.name}</h4>
                <div className="mt-1.5 font-mono text-[11px] space-y-0.5 text-slate-300">
                  <div>Capacity: <span className="text-white font-bold">{camp.current_occupancy} / {camp.total_capacity}</span></div>
                  <div>Available Beds: <span className="text-emerald-400 font-bold">{camp.available_beds}</span></div>
                  <div>Food Rations: <span className="text-cyan-400 font-bold">{camp.food_packets} pkts</span></div>
                  <div>Doctors On-Site: <span className="text-white font-bold">{camp.doctors_on_site}</span></div>
                </div>
              </div>
            </Popup>
          </Marker>
        ))}

        {/* 6. Render River Sensors */}
        {sensors.map((s) => (
          <Marker
            key={s.id}
            position={[s.latitude, s.longitude]}
            icon={createSensorIcon(s.status)}
          >
            <Popup>
              <div className="text-xs p-1">
                <span className="font-mono text-[10px] text-emerald-400 font-bold">HYDROLOGIC SENSOR</span>
                <h4 className="font-bold text-slate-100 text-xs mt-0.5">{s.station_name}</h4>
                <div className="mt-1.5 font-mono text-[11px] space-y-0.5 text-slate-300">
                  <div>Water Level: <span className="text-red-400 font-bold">{s.water_level_meters}m</span> (Danger: {s.danger_mark_meters}m)</div>
                  <div>Trend: <span className="text-amber-400 font-bold">{s.trend}</span></div>
                  <div>3h Rainfall: <span className="text-cyan-400 font-bold">{s.rainfall_mm_last_3h} mm</span></div>
                </div>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
};
