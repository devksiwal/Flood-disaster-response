import React from 'react';
import { FloodSensor } from '../types';
import { Waves, TrendingUp, TrendingDown, Minus, CloudRain } from 'lucide-react';

interface FloodAnalyticsProps {
  sensors: FloodSensor[];
  onSimulateRise: (sensorId: string, currentLevel: number) => void;
}

export const FloodAnalytics: React.FC<FloodAnalyticsProps> = ({ sensors, onSimulateRise }) => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg p-3.5 flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-2.5 mb-3">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300">
            <Waves className="w-3.5 h-3.5" />
          </div>
          <div>
            <h3 className="text-xs font-semibold text-slate-100">
              River Hydrology & Basin Gauging
            </h3>
            <p className="text-[11px] text-slate-400">
              Telemetry from {sensors.length} hydrometric telemetry stations
            </p>
          </div>
        </div>
      </div>

      {/* Grid of Gauging Stations */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2.5 overflow-y-auto max-h-[420px] pr-1">
        {sensors.map((s) => {
          const isDanger = s.water_level_meters >= s.danger_mark_meters;
          const isWarning = s.water_level_meters >= s.warning_level_meters && !isDanger;
          const diffFromDanger = roundToTwo(s.water_level_meters - s.danger_mark_meters);

          return (
            <div
              key={s.id}
              className="p-3 rounded bg-slate-950 border border-slate-800"
            >
              {/* Station Code & Status */}
              <div className="flex items-start justify-between gap-2 mb-1.5">
                <div>
                  <span className="text-[10px] font-mono font-medium text-slate-400 bg-slate-900 px-1.5 py-0.5 rounded border border-slate-800">
                    {s.station_code}
                  </span>
                  <h4 className="text-xs font-medium text-slate-100 mt-1 line-clamp-1">{s.station_name}</h4>
                  <p className="text-[10px] text-slate-400">{s.river_basin}</p>
                </div>

                <span
                  className={`px-1.5 py-0.5 rounded text-[10px] font-medium border ${
                    isDanger
                      ? 'bg-red-500/10 text-red-400 border-red-500/20'
                      : isWarning
                      ? 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                      : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                  }`}
                >
                  {s.status}
                </span>
              </div>

              {/* Water Level Gauge Display */}
              <div className="bg-slate-900 p-2 rounded border border-slate-850 my-2">
                <div className="flex items-baseline justify-between">
                  <span className="text-[10px] text-slate-400">Water Gauge:</span>
                  <div className="flex items-baseline gap-1">
                    <span
                      className={`text-sm font-semibold font-mono ${
                        isDanger ? 'text-red-400' : isWarning ? 'text-amber-400' : 'text-slate-100'
                      }`}
                    >
                      {s.water_level_meters} m
                    </span>
                    {s.trend === 'RISING' ? (
                      <TrendingUp className="w-3.5 h-3.5 text-red-400" />
                    ) : s.trend === 'RECEDING' ? (
                      <TrendingDown className="w-3.5 h-3.5 text-emerald-400" />
                    ) : (
                      <Minus className="w-3.5 h-3.5 text-slate-400" />
                    )}
                  </div>
                </div>

                <div className="text-[10px] font-mono text-slate-400 flex items-center justify-between mt-1 pt-1 border-t border-slate-800">
                  <span>Danger: {s.danger_mark_meters}m</span>
                  <span className={diffFromDanger > 0 ? 'text-red-400 font-medium' : 'text-slate-400'}>
                    {diffFromDanger > 0 ? `+${diffFromDanger}m Above` : `${Math.abs(diffFromDanger)}m Below`}
                  </span>
                </div>
              </div>

              {/* Rain & Discharge Stats */}
              <div className="grid grid-cols-2 gap-1.5 text-[10px] font-mono text-slate-400 mb-2">
                <div className="flex items-center gap-1 bg-slate-900 p-1 rounded border border-slate-850">
                  <CloudRain className="w-3 h-3 text-slate-400" />
                  <span>3h: <strong className="text-slate-200">{s.rainfall_mm_last_3h}mm</strong></span>
                </div>
                <div className="flex items-center gap-1 bg-slate-900 p-1 rounded border border-slate-850">
                  <Waves className="w-3 h-3 text-slate-400" />
                  <span>{Math.round(s.discharge_cusecs / 1000)}k cusecs</span>
                </div>
              </div>

              {/* Simulation Trigger */}
              <div className="flex justify-end pt-1.5 border-t border-slate-850">
                <button
                  onClick={() => onSimulateRise(s.id, s.water_level_meters)}
                  className="px-2 py-0.5 text-[10px] font-mono bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded transition-colors text-slate-300"
                >
                  Simulate +0.4m Surge
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

function roundToTwo(num: number): number {
  return Math.round((num + Number.EPSILON) * 100) / 100;
}
