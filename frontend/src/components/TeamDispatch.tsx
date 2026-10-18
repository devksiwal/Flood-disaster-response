import React from 'react';
import { Team } from '../types';
import { Shield, Radio, Anchor, Truck, Cross, Plane } from 'lucide-react';

interface TeamDispatchProps {
  teams: Team[];
  onUpdateTeamStatus: (teamId: string, status: string) => void;
}

export const TeamDispatch: React.FC<TeamDispatchProps> = ({ teams, onUpdateTeamStatus }) => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg p-3.5 flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-2.5 mb-3">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300">
            <Shield className="w-3.5 h-3.5" />
          </div>
          <div>
            <h3 className="text-xs font-semibold text-slate-100">
              Rescue Fleet & Battalion Readiness
            </h3>
            <p className="text-[11px] text-slate-400">
              Deployment matrix across {teams.length} response battalions
            </p>
          </div>
        </div>
      </div>

      {/* Grid of Teams */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2.5 overflow-y-auto max-h-[420px] pr-1">
        {teams.map((team) => {
          const isAvailable = team.status === 'AVAILABLE';
          const isDispatched = team.status === 'DISPATCHED';
          return (
            <div
              key={team.id}
              className={`p-3 rounded border transition-colors ${
                isDispatched
                  ? 'border-slate-700 bg-slate-900/90'
                  : 'border-slate-800 bg-slate-950'
              }`}
            >
              {/* Callsign & Status */}
              <div className="flex items-start justify-between gap-2 mb-2">
                <div>
                  <span className="text-[10px] font-mono font-medium text-slate-400 bg-slate-900 px-1.5 py-0.5 rounded border border-slate-800">
                    {team.agency}
                  </span>
                  <h4 className="text-xs font-medium text-slate-100 mt-1 line-clamp-1">{team.callsign}</h4>
                </div>

                <span
                  className={`px-1.5 py-0.5 rounded text-[10px] font-medium border ${
                    isAvailable
                      ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                      : isDispatched
                      ? 'bg-blue-500/10 text-blue-400 border-blue-500/20'
                      : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                  }`}
                >
                  {team.status}
                </span>
              </div>

              {/* Base & Radio */}
              <div className="text-[11px] text-slate-400 space-y-0.5 mb-2 font-mono">
                <div className="text-slate-300 truncate">Base: {team.base_station}</div>
                <div className="flex items-center gap-1 text-slate-400">
                  <Radio className="w-3 h-3 text-slate-500" />
                  <span>{team.contact_radio}</span>
                </div>
              </div>

              {/* Equipment Capabilities Grid */}
              <div className="grid grid-cols-4 gap-1 bg-slate-900 p-1.5 rounded border border-slate-800/80 text-center font-mono text-[10px] text-slate-300">
                <div className="flex flex-col items-center">
                  <Anchor className="w-3 h-3 text-slate-400 mb-0.5" />
                  <span className="font-medium text-slate-200">{team.boats_count}</span>
                  <span className="text-[9px] text-slate-500">Boats</span>
                </div>
                <div className="flex flex-col items-center">
                  <Truck className="w-3 h-3 text-slate-400 mb-0.5" />
                  <span className="font-medium text-slate-200">{team.amphibious_vehicles}</span>
                  <span className="text-[9px] text-slate-500">Amphib</span>
                </div>
                <div className="flex flex-col items-center">
                  <Cross className="w-3 h-3 text-slate-400 mb-0.5" />
                  <span className="font-medium text-slate-200">{team.medical_kits}</span>
                  <span className="text-[9px] text-slate-500">MedKits</span>
                </div>
                <div className="flex flex-col items-center">
                  <Plane className="w-3 h-3 text-slate-400 mb-0.5" />
                  <span className="font-medium text-slate-200">{team.drones_count}</span>
                  <span className="text-[9px] text-slate-500">Drones</span>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center justify-between mt-2 pt-2 border-t border-slate-800/80 text-[10px] font-mono">
                {team.current_incident_id ? (
                  <span className="text-slate-400">Mission: {team.current_incident_id}</span>
                ) : (
                  <span className="text-slate-500">Standby</span>
                )}

                <button
                  onClick={() => onUpdateTeamStatus(team.id, isAvailable ? 'ON_MISSION' : 'AVAILABLE')}
                  className="px-2 py-0.5 rounded font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors"
                >
                  {isAvailable ? 'Dispatch' : 'Set Available'}
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
