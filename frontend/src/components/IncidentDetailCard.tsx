import React from 'react';
import { Incident, Team, ReliefCamp, RescueRoute } from '../types';
import {
  AlertCircle,
  Shield,
  Home,
  Navigation,
  Radio,
  Play,
  CheckCircle,
  Users,
  Droplets,
  Clock,
  Package,
  HeartPulse,
  MapPin,
  Send,
  Sparkles,
} from 'lucide-react';

interface IncidentDetailCardProps {
  incident: Incident | null;
  assignedTeam?: Team | null;
  assignedCamp?: ReliefCamp | null;
  route?: RescueRoute | null;
  onTriggerPipeline: (incidentId: string) => void;
  onUpdateStatus: (incidentId: string, status: string) => void;
  onCenterMap?: (lat: number, lng: number) => void;
}

export const IncidentDetailCard: React.FC<IncidentDetailCardProps> = ({
  incident,
  assignedTeam,
  assignedCamp,
  route,
  onTriggerPipeline,
  onUpdateStatus,
  onCenterMap,
}) => {
  if (!incident) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-lg p-6 text-center flex flex-col items-center justify-center h-full min-h-[300px]">
        <div className="w-10 h-10 rounded-full bg-slate-800 flex items-center justify-center text-slate-500 mb-2">
          <AlertCircle className="w-5 h-5" />
        </div>
        <h4 className="text-sm font-medium text-slate-200">No Incident Selected</h4>
        <p className="text-xs text-slate-400 mt-1 max-w-xs">
          Select an incident on the map or from the quick selector to inspect the complete 6-agent AI response breakdown.
        </p>
      </div>
    );
  }

  const isCritical = incident.priority_level === 'CRITICAL';
  const isRescued = incident.status === 'RESCUED';

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg p-4 flex flex-col h-full overflow-y-auto max-h-[580px]">
      {/* Top Header: ID, Title & Status */}
      <div className="flex items-start justify-between gap-3 border-b border-slate-800 pb-3 mb-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="font-mono text-xs font-semibold text-slate-200 bg-slate-800 px-1.5 py-0.5 rounded border border-slate-700">
              {incident.id}
            </span>
            <span
              className={`text-[10px] font-medium px-2 py-0.5 rounded border ${
                isCritical
                  ? 'bg-red-500/10 text-red-400 border-red-500/20'
                  : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
              }`}
            >
              {incident.priority_level} Urgency ({incident.priority_score}/100)
            </span>
            <span className="text-[10px] text-slate-400 font-mono bg-slate-950 px-1.5 py-0.5 rounded border border-slate-800">
              Status: {incident.status}
            </span>
          </div>
          <h3 className="text-sm font-semibold text-slate-100 mt-1.5">{incident.title}</h3>
          <div className="flex items-center gap-1.5 text-xs text-slate-400 mt-0.5">
            <MapPin className="w-3.5 h-3.5 text-slate-400" />
            <span>{incident.location_name}</span>
            {onCenterMap && (
              <button
                onClick={() => onCenterMap(incident.latitude, incident.longitude)}
                className="text-[11px] text-slate-400 hover:text-slate-200 underline ml-1"
              >
                (View on Map)
              </button>
            )}
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => onTriggerPipeline(incident.id)}
            title="Re-run Multi-Agent Pipeline"
            className="flex items-center gap-1 px-2.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded text-xs font-medium transition-colors"
          >
            <Play className="w-3 h-3 text-emerald-400" />
            <span>Re-Run AI</span>
          </button>
          {!isRescued && (
            <button
              onClick={() => onUpdateStatus(incident.id, 'RESCUED')}
              className="flex items-center gap-1 px-2.5 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded text-xs font-medium transition-colors"
            >
              <CheckCircle className="w-3 h-3" />
              <span>Mark Rescued</span>
            </button>
          )}
        </div>
      </div>

      {/* Distress SOS Message Excerpt */}
      <div className="bg-slate-950 p-2.5 rounded border border-slate-850 mb-3 text-xs">
        <span className="text-[10px] uppercase font-medium text-slate-400 block mb-0.5">
          Citizen Distress SOS Transcript
        </span>
        <p className="text-slate-300 italic">"{incident.raw_sos}"</p>
      </div>

      {/* 6-Stage Agent Decision Summary (Plain English) */}
      <div className="space-y-2.5 text-xs flex-1">
        <h4 className="text-[11px] uppercase font-semibold text-slate-400 tracking-wider">
          6-Agent Autonomous Decision Breakdown
        </h4>

        {/* Step 1 & 2: Detection & Priority Triage */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {/* Detection */}
          <div className="p-2.5 rounded bg-slate-950 border border-slate-800">
            <div className="flex items-center gap-1.5 text-[11px] font-medium text-slate-300 mb-1">
              <span className="font-mono text-slate-400">01.</span>
              <span>Distress Triage (Extraction)</span>
            </div>
            <div className="text-[11px] text-slate-400 space-y-0.5">
              <div>
                Victims: <strong className="text-slate-200">{incident.victim_count}</strong> ({incident.children_count} children, {incident.elderly_count} elderly, {incident.injured_count} injured)
              </div>
              <div>
                Water Depth: <strong className="text-slate-200">{incident.water_depth_meters}m</strong>
              </div>
              {incident.hazards && incident.hazards.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-1">
                  {incident.hazards.map((h, i) => (
                    <span key={i} className="text-[9px] px-1 rounded bg-slate-900 border border-slate-800 text-slate-300">
                      {h.replace(/_/g, ' ')}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Priority */}
          <div className="p-2.5 rounded bg-slate-950 border border-slate-800">
            <div className="flex items-center gap-1.5 text-[11px] font-medium text-slate-300 mb-1">
              <span className="font-mono text-slate-400">02.</span>
              <span>Priority & MCDA Scoring</span>
            </div>
            <div className="text-[11px] text-slate-400 space-y-0.5">
              <div>
                Calculated Score: <strong className="text-slate-200">{incident.priority_score} / 100</strong>
              </div>
              <div>
                Urgency Class: <strong className="text-slate-200">{incident.priority_level}</strong>
              </div>
              <div>
                Dispatch SLA: <strong className="text-slate-200">{isCritical ? '15 minutes' : '45 minutes'}</strong>
              </div>
            </div>
          </div>
        </div>

        {/* Step 3 & 4: Resource Allocation & Route Planning */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {/* Resource Squad */}
          <div className="p-2.5 rounded bg-slate-950 border border-slate-800">
            <div className="flex items-center gap-1.5 text-[11px] font-medium text-slate-300 mb-1">
              <span className="font-mono text-slate-400">03.</span>
              <span>Dispatched Rescue Squad</span>
            </div>
            {assignedTeam ? (
              <div className="text-[11px] text-slate-400 space-y-0.5">
                <div className="font-medium text-slate-200 truncate">{assignedTeam.callsign}</div>
                <div>Agency: {assignedTeam.agency} • Radio: {assignedTeam.contact_radio}</div>
                <div>Fleet: {assignedTeam.boats_count} Boats, {assignedTeam.amphibious_vehicles} Amphibious</div>
              </div>
            ) : (
              <div className="text-[11px] text-slate-500 italic">Evaluating closest matching battalion...</div>
            )}
          </div>

          {/* Route Planning */}
          <div className="p-2.5 rounded bg-slate-950 border border-slate-800">
            <div className="flex items-center gap-1.5 text-[11px] font-medium text-slate-300 mb-1">
              <span className="font-mono text-slate-400">04.</span>
              <span>Safe Navigation Corridor</span>
            </div>
            {route ? (
              <div className="text-[11px] text-slate-400 space-y-0.5">
                <div>Est. Distance: <strong className="text-slate-200">{route.distance_km} km</strong></div>
                <div>Transit Time: <strong className="text-slate-200">~{route.estimated_minutes} mins</strong></div>
                <div className="text-slate-400 text-[10px] truncate">{route.route_summary}</div>
              </div>
            ) : (
              <div className="text-[11px] text-slate-500 italic">Calculating safe path avoiding flood zones...</div>
            )}
          </div>
        </div>

        {/* Step 5 & 6: Relief Camp Logistics & Multi-Channel Communications */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {/* Relief Camp Logistics */}
          <div className="p-2.5 rounded bg-slate-950 border border-slate-800">
            <div className="flex items-center gap-1.5 text-[11px] font-medium text-slate-300 mb-1">
              <span className="font-mono text-slate-400">05.</span>
              <span>Relief Shelter Quotas</span>
            </div>
            {assignedCamp ? (
              <div className="text-[11px] text-slate-400 space-y-0.5">
                <div className="font-medium text-slate-200 truncate">{assignedCamp.name}</div>
                <div>Beds Allocated: <strong className="text-slate-200">{incident.victim_count} beds</strong></div>
                <div>Supply Quota: <strong className="text-slate-200">{incident.victim_count * 4}L Water</strong>, <strong className="text-slate-200">{incident.victim_count * 3} Rations</strong></div>
              </div>
            ) : (
              <div className="text-[11px] text-slate-400 space-y-0.5">
                <div>Shelter: Sarada Girls Higher Sec. School</div>
                <div>Reserved: {incident.victim_count} beds, {incident.victim_count * 4}L potable water</div>
              </div>
            )}
          </div>

          {/* Communications */}
          <div className="p-2.5 rounded bg-slate-950 border border-slate-800">
            <div className="flex items-center gap-1.5 text-[11px] font-medium text-slate-300 mb-1">
              <span className="font-mono text-slate-400">06.</span>
              <span>Emergency Alerts Broadcast</span>
            </div>
            <div className="text-[11px] text-slate-400 space-y-0.5">
              <div>Citizen SMS: <span className="text-emerald-400 font-medium">Reassurance & ETA Dispatched</span></div>
              <div>Field Radio: <span className="text-slate-200">VHF Order Transmitted</span></div>
              <div>DEOC SITREP: <span className="text-slate-200">Incident File Synced</span></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
