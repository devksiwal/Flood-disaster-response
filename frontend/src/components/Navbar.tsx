import React, { useState, useEffect } from 'react';
import { Shield, Radio, Clock, PlusCircle } from 'lucide-react';

interface NavbarProps {
  onOpenSOSModal: () => void;
  onOpenGuideModal?: () => void;
  activeIncidentCount: number;
  deployedTeamsCount: number;
  criticalSensorsCount: number;
  viewMode: 'EOC' | 'CITIZEN';
  onToggleViewMode: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  onOpenSOSModal,
  onOpenGuideModal,
  activeIncidentCount,
  deployedTeamsCount,
  criticalSensorsCount,
  viewMode,
  onToggleViewMode,
}) => {
  const [localTimeStr, setLocalTimeStr] = useState<string>('');
  const [utcTimeStr, setUtcTimeStr] = useState<string>('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      const localTime = now.toLocaleTimeString('en-GB', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
      const localDate = now.toLocaleDateString('en-GB', { weekday: 'short', day: '2-digit', month: 'short', year: 'numeric' });
      const tzShort = new Intl.DateTimeFormat('en-US', { timeZoneName: 'short' }).formatToParts(now).find(p => p.type === 'timeZoneName')?.value || 'IST';

      const utcHours = String(now.getUTCHours()).padStart(2, '0');
      const utcMins = String(now.getUTCMinutes()).padStart(2, '0');
      const utcSecs = String(now.getUTCSeconds()).padStart(2, '0');

      setLocalTimeStr(`${localDate} ${localTime} ${tzShort}`);
      setUtcTimeStr(`${utcHours}:${utcMins}:${utcSecs}`);
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="bg-slate-900 border-b border-slate-800 sticky top-0 z-50 px-4 lg:px-6 py-2.5">
      <div className="max-w-[1920px] mx-auto flex flex-col md:flex-row items-center justify-between gap-3">
        {/* Brand & Authority */}
        <div className="flex items-center gap-3 w-full md:w-auto justify-between md:justify-start">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-200">
              <Shield className="w-4 h-4 text-slate-200" />
            </div>

            <div>
              <div className="flex items-center gap-2">
                <span className="text-[11px] font-medium tracking-wide uppercase text-slate-400">
                  NDMA Emergency Operations
                </span>
                <span className="inline-flex items-center text-[11px] font-medium text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-1.5 py-0.2 rounded">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mr-1.5"></span>
                  Active Response Level 2
                </span>
              </div>
              <h1 className="text-sm lg:text-base font-semibold text-slate-100 flex items-center gap-2">
                Flood Disaster Response System
                <span className="text-xs font-normal text-slate-400 hidden xl:inline">
                  (6-Agent Autonomous Pipeline)
                </span>
              </h1>
            </div>
          </div>
        </div>

        {/* Tactical Indicators & Actions */}
        <div className="flex flex-wrap items-center gap-2.5 lg:gap-4 w-full md:w-auto justify-end">
          {/* Telemetry Pills */}
          <div className="hidden sm:flex items-center gap-3 text-xs bg-slate-950 px-3 py-1.5 rounded border border-slate-800">
            <div className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-red-400"></span>
              <span className="text-slate-400">Incidents:</span>
              <span className="text-slate-200 font-medium">{activeIncidentCount}</span>
            </div>
            <div className="h-3 w-px bg-slate-800"></div>
            <div className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
              <span className="text-slate-400">Teams:</span>
              <span className="text-slate-200 font-medium">{deployedTeamsCount}</span>
            </div>
            <div className="h-3 w-px bg-slate-800"></div>
            <div className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
              <span className="text-slate-400">Danger Stations:</span>
              <span className="text-slate-200 font-medium">{criticalSensorsCount}</span>
            </div>
          </div>

          {/* Time */}
          <div className="hidden lg:flex items-center gap-2 text-xs text-slate-400 bg-slate-950 px-2.5 py-1.5 rounded border border-slate-800">
            <Clock className="w-3.5 h-3.5 text-slate-400" />
            <span className="text-slate-200 font-mono">{localTimeStr || 'SYNCING'}</span>
            {utcTimeStr && (
              <span className="text-[10px] text-slate-400 bg-slate-900 px-1 py-0.5 rounded border border-slate-800 font-mono">
                UTC {utcTimeStr}
              </span>
            )}
          </div>

          {/* Live Stream Status */}
          <div className="flex items-center gap-1.5 text-xs text-slate-300 bg-slate-950 px-2 py-1.5 rounded border border-slate-800">
            <Radio className="w-3.5 h-3.5 text-emerald-400" />
            <span className="hidden sm:inline text-xs font-medium">Live Telemetry</span>
          </div>

          {/* How It Works Guide Button */}
          {onOpenGuideModal && (
            <button
              onClick={onOpenGuideModal}
              className="flex items-center gap-1.5 text-xs font-medium px-2.5 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors"
              title="Learn how the 6 AI agents coordinate"
            >
              <span>How AI Works</span>
            </button>
          )}

          {/* View Switcher Button */}
          <button
            onClick={onToggleViewMode}
            className="flex items-center gap-1.5 text-xs font-medium px-2.5 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors"
          >
            {viewMode === 'EOC' ? (
              <span>Citizen 112 Portal</span>
            ) : (
              <span>EOC Command Radar</span>
            )}
          </button>

          {viewMode === 'EOC' && (
            <button
              onClick={onOpenSOSModal}
              className="flex items-center gap-1.5 bg-red-600 hover:bg-red-500 text-white text-xs font-medium px-3.5 py-1.5 rounded border border-red-500/30 transition-colors"
            >
              <PlusCircle className="w-3.5 h-3.5" />
              <span>Submit SOS</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
};
