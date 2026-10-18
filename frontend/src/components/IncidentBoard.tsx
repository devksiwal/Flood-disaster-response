import React, { useState, useMemo } from 'react';
import { Incident } from '../types';
import { AlertCircle, Users, Droplets, MapPin, Play, Check, Search } from 'lucide-react';

interface IncidentBoardProps {
  incidents: Incident[];
  selectedIncidentId?: string | null;
  onSelectIncident: (id: string) => void;
  onTriggerPipeline: (id: string) => void;
  onUpdateStatus: (id: string, status: string) => void;
}

export const IncidentBoard: React.FC<IncidentBoardProps> = ({
  incidents,
  selectedIncidentId,
  onSelectIncident,
  onTriggerPipeline,
  onUpdateStatus,
}) => {
  const [filter, setFilter] = useState<'ALL' | 'CRITICAL' | 'DISPATCHED' | 'RESCUED'>('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  const filteredIncidents = useMemo(() => {
    return incidents.filter((i) => {
      if (filter === 'CRITICAL' && i.priority_level !== 'CRITICAL') return false;
      if (filter === 'DISPATCHED' && i.status !== 'DISPATCHED') return false;
      if (filter === 'RESCUED' && i.status !== 'RESCUED') return false;

      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase();
        const matchesLocation = i.location_name?.toLowerCase().includes(query);
        const matchesTitle = i.title?.toLowerCase().includes(query);
        const matchesSos = i.raw_sos?.toLowerCase().includes(query);
        const matchesId = i.id?.toLowerCase().includes(query);
        const matchesTeam = i.assigned_team_id?.toLowerCase().includes(query);
        return matchesLocation || matchesTitle || matchesSos || matchesId || matchesTeam;
      }
      return true;
    });
  }, [incidents, filter, searchQuery]);

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg p-3.5 flex flex-col h-full">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800 pb-2.5 mb-3">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300">
            <AlertCircle className="w-3.5 h-3.5" />
          </div>
          <div>
            <h3 className="text-xs font-semibold text-slate-100">
              Distress Incident Triage Queue
            </h3>
            <p className="text-[11px] text-slate-400">
              Showing {filteredIncidents.length} of {incidents.length} incidents
            </p>
          </div>
        </div>

        {/* Search & Filter Controls */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Search Box */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2 top-2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search location, hazards, ID..."
              className="bg-slate-950 border border-slate-800 rounded pl-7 pr-2 py-1 text-[11px] text-slate-200 focus:outline-none focus:border-slate-700 w-44 sm:w-56"
            />
          </div>

          {/* Filter Tabs */}
          <div className="flex items-center gap-1 bg-slate-950 p-1 rounded border border-slate-800 text-[11px]">
            {(['ALL', 'CRITICAL', 'DISPATCHED', 'RESCUED'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setFilter(tab)}
                className={`px-2 py-0.5 rounded transition-colors ${
                  filter === tab
                    ? 'bg-slate-800 text-slate-100 font-medium'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>
      </div>


      {/* Incident List */}
      <div className="flex-1 overflow-y-auto space-y-2 pr-1 max-h-[500px]">
        {filteredIncidents.length === 0 ? (
          <div className="py-12 text-center text-slate-500 font-mono text-xs">
            No incidents found in this filter category.
          </div>
        ) : (
          filteredIncidents.map((inc) => {
            const isSelected = inc.id === selectedIncidentId;
            const isCritical = inc.priority_level === 'CRITICAL';
            return (
              <div
                key={inc.id}
                onClick={() => onSelectIncident(inc.id)}
                className={`p-3 rounded border transition-colors cursor-pointer ${
                  isSelected
                    ? 'border-slate-600 bg-slate-850'
                    : 'border-slate-800 bg-slate-950 hover:border-slate-700'
                }`}
              >
                {/* Top Row */}
                <div className="flex items-center justify-between gap-2 mb-1.5">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-medium text-slate-300">{inc.id}</span>
                    <span className="text-[10px] text-slate-400 bg-slate-900 px-1.5 py-0.2 rounded border border-slate-800">
                      {inc.category.replace('_', ' ')}
                    </span>
                  </div>

                  <span
                    className={`px-1.5 py-0.2 rounded text-[10px] font-mono font-medium border ${
                      isCritical
                        ? 'bg-red-500/10 text-red-400 border-red-500/20'
                        : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                    }`}
                  >
                    {inc.priority_level} ({inc.priority_score})
                  </span>
                </div>

                {/* Title */}
                <h4 className="text-xs font-medium text-slate-100 line-clamp-1">{inc.title}</h4>

                {/* SOS Message */}
                <p className="text-[11px] text-slate-400 italic my-1.5 line-clamp-2 bg-slate-900 p-1.5 rounded border border-slate-850">
                  "{inc.raw_sos}"
                </p>

                {/* Demographics & Depth */}
                <div className="flex flex-wrap items-center gap-3 text-[11px] text-slate-400 mt-1.5">
                  <span className="flex items-center gap-1 text-slate-300">
                    <MapPin className="w-3 h-3 text-slate-400" />
                    {inc.location_name}
                  </span>
                  <span className="flex items-center gap-1 text-slate-300 font-mono">
                    <Droplets className="w-3 h-3 text-slate-400" />
                    {inc.water_depth_meters}m depth
                  </span>
                  <span className="flex items-center gap-1 text-slate-300 font-mono">
                    <Users className="w-3 h-3 text-slate-400" />
                    {inc.victim_count} victims
                  </span>
                </div>

                {/* Hazards Badges */}
                {inc.hazards && inc.hazards.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-1.5">
                    {inc.hazards.map((h, i) => (
                      <span
                        key={i}
                        className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-slate-900 text-slate-400 border border-slate-800"
                      >
                        {h.replace(/_/g, ' ')}
                      </span>
                    ))}
                  </div>
                )}

                {/* Actions Footer */}
                <div className="flex items-center justify-between border-t border-slate-800/80 pt-2 mt-2">
                  <div className="text-[10px] font-mono">
                    <span className="text-slate-500">Status: </span>
                    <span className="text-slate-200 font-medium">{inc.status}</span>
                    {inc.assigned_team_id && (
                      <span className="text-slate-500 ml-1">({inc.assigned_team_id})</span>
                    )}
                  </div>

                  <div className="flex items-center gap-1.5" onClick={(e) => e.stopPropagation()}>
                    <button
                      onClick={() => onTriggerPipeline(inc.id)}
                      title="Re-run Multi-Agent Pipeline"
                      className="p-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors"
                    >
                      <Play className="w-3 h-3" />
                    </button>
                    {inc.status !== 'RESCUED' && (
                      <button
                        onClick={() => onUpdateStatus(inc.id, 'RESCUED')}
                        className="px-2 py-0.5 text-[10px] font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded transition-colors"
                      >
                        Mark Rescued
                      </button>
                    )}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
