import React from 'react';
import { X, Search, Activity, Shield, Navigation, Home, Radio, ArrowRight, CheckCircle2 } from 'lucide-react';

interface HowItWorksModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const AGENT_WORKFLOW_STEPS = [
  {
    step: '01',
    name: 'Emergency Detection Agent',
    icon: Search,
    title: 'Deciphers Distress Messages',
    description:
      'Ingests chaotic citizen calls, 112 text transmissions, and voice transcripts. Extracts key metrics: exact trapped victim count (adults, infants, elderly, injured), water depth in meters, landmarks, and live hazards.',
  },
  {
    step: '02',
    name: 'Priority Agent',
    icon: Activity,
    title: 'Calculates Mathematical Urgency (0–100)',
    description:
      'Uses Multi-Criteria Decision Analysis (MCDA) to weigh water rise speed, casualty vulnerability, and hazards (submerged power lines, structural collapse) so emergency responders prioritize the most urgent lives during the golden hour.',
  },
  {
    step: '03',
    name: 'Resource Allocation Agent',
    icon: Shield,
    title: 'Dispatches Best-Equipped Battalion',
    description:
      'Searches real-time manifests across NDRF, SDRF, and Coast Guard units. Matches gear requirements (Zodiac inflatable boats, amphibious trucks, drones, medical kits) and proximity to send the optimal squad.',
  },
  {
    step: '04',
    name: 'Route Planning Agent',
    icon: Navigation,
    title: 'Charts Flood-Avoidance Corridors',
    description:
      'Analyzes live GIS flood risk polygons and submerged chokepoints. Generates safe transit waypoints guiding the rescue boat from base station -> victim -> nearest highland evacuation shelter.',
  },
  {
    step: '05',
    name: 'Relief Camp Logistics Agent',
    icon: Home,
    title: 'Reserves Shelter Beds & Supplies',
    description:
      'Allocates shelter beds at safe highland relief centers. Calculates humanitarian supply quotas (4L drinking water/person, 3 meal packets/person) and triggers inter-shelter supply trucks or medical doctor reinforcements.',
  },
  {
    step: '06',
    name: 'Communication Agent',
    icon: Radio,
    title: 'Broadcasts Synchronized Directives',
    description:
      'Simultaneously sends 4 synchronized messages: Reassurance SMS with team ETA to the trapped citizen, tactical dispatch order to the team VHF radio, official SITREP to the DEOC Command Center, and camp intake advisory to shelter staff.',
  },
];

export const HowItWorksModal: React.FC<HowItWorksModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[2000] flex items-center justify-center p-4 bg-black/75">
      <div className="bg-slate-900 border border-slate-700 rounded-lg w-full max-w-3xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="p-4 bg-slate-950 border-b border-slate-800 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-slate-100 flex items-center gap-2">
              <span>System Guide: How the 6 AI Agents Coordinate</span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              End-to-end automated disaster response lifecycle from citizen SOS to safe shelter arrival
            </p>
          </div>

          <button
            onClick={onClose}
            className="p-1 rounded text-slate-400 hover:text-slate-200 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Workflow Steps Grid */}
        <div className="p-4 overflow-y-auto space-y-3">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {AGENT_WORKFLOW_STEPS.map((step) => {
              const Icon = step.icon;
              return (
                <div
                  key={step.step}
                  className="p-3 rounded bg-slate-950 border border-slate-800 flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between mb-1.5">
                      <div className="flex items-center gap-2">
                        <div className="w-6 h-6 rounded bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-300">
                          <Icon className="w-3.5 h-3.5" />
                        </div>
                        <span className="text-[11px] font-mono font-medium text-slate-400">
                          Agent {step.step}
                        </span>
                      </div>
                      <span className="text-[10px] text-slate-500 font-mono">Sequential Chain</span>
                    </div>

                    <h4 className="text-xs font-medium text-slate-100">{step.title}</h4>
                    <span className="text-[10px] text-slate-400 block mb-1">({step.name})</span>
                    <p className="text-[11px] text-slate-400 leading-relaxed">{step.description}</p>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Quick Summary Banner */}
          <div className="p-3 rounded bg-slate-950 border border-slate-800 flex items-center justify-between text-xs text-slate-300">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>
                <strong>100% Autonomous & Offline Capable:</strong> The system executes this complete 6-stage chain in under 200ms per incident.
              </span>
            </div>
            <button
              onClick={onClose}
              className="px-3 py-1 rounded text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors shrink-0 ml-3"
            >
              Got It
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
