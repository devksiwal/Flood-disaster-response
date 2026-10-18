import React, { useState } from 'react';
import { ReliefCamp } from '../types';
import { Home, Droplets, Package, HeartPulse, Phone } from 'lucide-react';

interface ReliefCampTrackerProps {
  camps: ReliefCamp[];
  onAdmitEvacuees: (campId: string, count: number) => void;
}

export const ReliefCampTracker: React.FC<ReliefCampTrackerProps> = ({ camps, onAdmitEvacuees }) => {
  const [admitCounts, setAdmitCounts] = useState<{ [key: string]: number }>({});

  const handleCountChange = (campId: string, count: number) => {
    setAdmitCounts((prev) => ({ ...prev, [campId]: count }));
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg p-3.5 flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-2.5 mb-3">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300">
            <Home className="w-3.5 h-3.5" />
          </div>
          <div>
            <h3 className="text-xs font-semibold text-slate-100">
              Relief Shelter & Supply Logistics
            </h3>
            <p className="text-[11px] text-slate-400">
              Coordinated by Relief Camp Logistics Agent ({camps.length} highland shelters)
            </p>
          </div>
        </div>
      </div>

      {/* Camp Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5 overflow-y-auto max-h-[420px] pr-1">
        {camps.map((camp) => {
          const occupancyRate = Math.min(
            100,
            Math.round((camp.current_occupancy / Math.max(1, camp.total_capacity)) * 100)
          );
          const isNearFull = occupancyRate >= 85;
          const admitCount = admitCounts[camp.id] || 10;

          return (
            <div
              key={camp.id}
              className="p-3 rounded bg-slate-950 border border-slate-800 flex flex-col justify-between"
            >
              <div>
                {/* Header: Name & Status */}
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div>
                    <span className="text-[10px] font-mono font-medium text-slate-400 bg-slate-900 px-1.5 py-0.5 rounded border border-slate-800">
                      {camp.id}
                    </span>
                    <h4 className="text-xs font-medium text-slate-100 mt-1">{camp.name}</h4>
                    <p className="text-[11px] text-slate-400">{camp.location_name}</p>
                  </div>

                  <span
                    className={`px-1.5 py-0.5 rounded text-[10px] font-medium border ${
                      camp.status === 'OPEN'
                        ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                        : 'bg-red-500/10 text-red-400 border-red-500/20'
                    }`}
                  >
                    {camp.status}
                  </span>
                </div>

                {/* Occupancy Progress Bar */}
                <div className="my-2 bg-slate-900 p-2 rounded border border-slate-800/80">
                  <div className="flex items-center justify-between text-[11px] font-mono mb-1">
                    <span className="text-slate-400">Occupancy:</span>
                    <span className="text-slate-200">
                      {camp.current_occupancy} / {camp.total_capacity} ({occupancyRate}%)
                    </span>
                  </div>
                  <div className="w-full bg-slate-800 h-1.5 rounded overflow-hidden">
                    <div
                      className={`h-full rounded transition-all duration-300 ${
                        isNearFull ? 'bg-amber-400' : 'bg-slate-300'
                      }`}
                      style={{ width: `${occupancyRate}%` }}
                    ></div>
                  </div>
                  <div className="text-[10px] text-slate-400 mt-1 flex justify-between">
                    <span>Available Capacity:</span>
                    <span className="font-mono text-slate-200 font-medium">{camp.available_beds} beds</span>
                  </div>
                </div>

                {/* Supply Logistics Manifest */}
                <div className="grid grid-cols-3 gap-1 bg-slate-900 p-1.5 rounded border border-slate-800/80 text-center font-mono text-[10px] text-slate-300 mb-2">
                  <div className="flex flex-col items-center">
                    <Package className="w-3 h-3 text-slate-400 mb-0.5" />
                    <span className="font-medium text-slate-200">{camp.food_packets}</span>
                    <span className="text-[9px] text-slate-500">Rations</span>
                  </div>
                  <div className="flex flex-col items-center">
                    <Droplets className="w-3 h-3 text-slate-400 mb-0.5" />
                    <span className="font-medium text-slate-200">{camp.drinking_water_liters}L</span>
                    <span className="text-[9px] text-slate-500">Water</span>
                  </div>
                  <div className="flex flex-col items-center">
                    <HeartPulse className="w-3 h-3 text-slate-400 mb-0.5" />
                    <span className="font-medium text-slate-200">{camp.doctors_on_site}</span>
                    <span className="text-[9px] text-slate-500">Doctors</span>
                  </div>
                </div>
              </div>

              {/* Intake Action Bar */}
              <div className="flex items-center justify-between border-t border-slate-800/80 pt-2 text-[10px]">
                <div className="flex items-center gap-1 text-slate-400 font-mono">
                  <Phone className="w-3 h-3 text-slate-500" />
                  <span>{camp.phone}</span>
                </div>

                <div className="flex items-center gap-1.5">
                  <select
                    value={admitCount}
                    onChange={(e) => handleCountChange(camp.id, parseInt(e.target.value))}
                    className="bg-slate-900 border border-slate-700 rounded px-1.5 py-0.5 text-[10px] text-slate-200"
                  >
                    <option value="5">+5</option>
                    <option value="10">+10</option>
                    <option value="25">+25</option>
                    <option value="50">+50</option>
                  </select>
                  <button
                    onClick={() => onAdmitEvacuees(camp.id, admitCount)}
                    disabled={camp.available_beds <= 0}
                    className="px-2 py-0.5 rounded font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors disabled:opacity-50"
                  >
                    Admit
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
