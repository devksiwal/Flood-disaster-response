import React, { useState } from 'react';
import { AgentLog } from '../types';
import { Terminal, Cpu, CheckCircle2, ChevronDown, ChevronUp } from 'lucide-react';

interface AgentTerminalProps {
  logs: AgentLog[];
  isPipelineRunning: boolean;
}

const AGENTS_LIST = [
  { id: 1, name: 'Detection', fullName: 'Emergency Detection Agent', role: 'Distress NLP Triage' },
  { id: 2, name: 'Priority', fullName: 'Priority Agent', role: 'MCDA Urgency Scoring' },
  { id: 3, name: 'Resource', fullName: 'Resource Allocation Agent', role: 'Fleet Optimization' },
  { id: 4, name: 'Routing', fullName: 'Route Planning Agent', role: 'GIS Flood Avoidance' },
  { id: 5, name: 'Camp Logistics', fullName: 'Relief Camp Logistics Agent', role: 'Supply & Shelter Quotas' },
  { id: 6, name: 'Communication', fullName: 'Communication Agent', role: 'Multi-Channel Alerts' },
];

export const AgentTerminal: React.FC<AgentTerminalProps> = ({ logs, isPipelineRunning }) => {
  const [selectedLogId, setSelectedLogId] = useState<number | null>(null);

  const latestLogs = logs.slice(0, 10);

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg p-3.5 flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-2.5 mb-3">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300">
            <Cpu className="w-3.5 h-3.5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-xs font-semibold text-slate-100">
                Autonomous Multi-Agent Pipeline
              </h3>
              {isPipelineRunning ? (
                <span className="inline-flex items-center text-[10px] text-amber-400 bg-amber-500/10 border border-amber-500/20 px-1.5 py-0.2 rounded font-mono">
                  Executing Pipeline
                </span>
              ) : (
                <span className="inline-flex items-center text-[10px] text-slate-400 bg-slate-800 px-1.5 py-0.2 rounded font-mono">
                  Standby
                </span>
              )}
            </div>
            <p className="text-[11px] text-slate-400">
              6-stage sequential reasoning pipeline with shared disaster memory
            </p>
          </div>
        </div>

        <div className="flex items-center gap-1.5 text-xs text-slate-400 bg-slate-950 px-2 py-1 rounded border border-slate-800 font-mono">
          <Terminal className="w-3 h-3 text-slate-400" />
          <span>{logs.length} Trace Logs</span>
        </div>
      </div>

      {/* 6-Agent Clean Architecture Strip */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2 mb-3">
        {AGENTS_LIST.map((agent) => {
          const hasLogged = logs.some(
            (l) => l.agent_name.includes(agent.fullName) || agent.fullName.includes(l.agent_name)
          );
          return (
            <div
              key={agent.id}
              className={`p-2 rounded border transition-colors ${
                isPipelineRunning
                  ? 'border-slate-700 bg-slate-850'
                  : hasLogged
                  ? 'border-slate-700 bg-slate-800/80 text-slate-200'
                  : 'border-slate-800/80 bg-slate-950/60 text-slate-400'
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-[10px] font-mono font-medium text-slate-400">
                  0{agent.id}
                </span>
                {hasLogged && (
                  <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                )}
              </div>
              <div className="text-[11px] font-medium text-slate-200 truncate">{agent.name}</div>
              <div className="text-[10px] text-slate-400 truncate">{agent.role}</div>
            </div>
          );
        })}
      </div>

      {/* Reasoning Logs */}
      <div className="flex-1 overflow-y-auto space-y-2 pr-1 max-h-[350px]">
        {latestLogs.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-10 text-slate-500 text-xs text-center font-mono">
            <span>Agent Pipeline Standing By</span>
            <span className="text-[11px] text-slate-600 mt-0.5">
              Submit an incident SOS to trigger live sequential agent execution.
            </span>
          </div>
        ) : (
          latestLogs.map((log, idx) => {
            const isExpanded = selectedLogId === log.id;
            return (
              <div
                key={log.id || idx}
                className="p-2.5 rounded bg-slate-950 border border-slate-800 text-xs font-mono"
              >
                <div className="flex items-center justify-between gap-2 mb-1.5">
                  <div className="flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-slate-400"></span>
                    <span className="font-medium text-slate-200">{log.agent_name}</span>
                    <span className="text-[10px] text-slate-500">• {log.step}</span>
                  </div>
                  <div className="flex items-center gap-2 text-[10px] text-slate-400">
                    <span>{log.confidence ? `${Math.round(log.confidence * 100)}% conf` : '98% conf'}</span>
                    <span>{log.execution_time_ms}ms</span>
                  </div>
                </div>

                {/* Agent Thought */}
                <div className="bg-slate-900 p-2 rounded border border-slate-800 text-slate-300 font-sans text-xs leading-normal my-1">
                  <span className="font-mono text-slate-400 font-medium text-[10px] mr-1.5">[THOUGHT]:</span>
                  {log.thought}
                </div>

                {/* Action & Toggle */}
                <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1">
                  <div className="flex items-center gap-1.5">
                    <span className="text-slate-400">ACTION:</span>
                    <span className="bg-slate-850 text-slate-200 px-1.5 py-0.5 rounded border border-slate-800 text-[10px] font-mono">
                      {log.action}
                    </span>
                    {log.incident_id && (
                      <span className="text-slate-500 text-[10px]">({log.incident_id})</span>
                    )}
                  </div>

                  <button
                    onClick={() => setSelectedLogId(isExpanded ? null : log.id)}
                    className="text-slate-400 hover:text-slate-200 text-[10px] flex items-center gap-0.5"
                  >
                    <span>{isExpanded ? 'Hide Payload' : 'Inspect JSON'}</span>
                    {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                  </button>
                </div>

                {/* Expandable JSON Payload */}
                {isExpanded && (
                  <div className="mt-2 p-2 bg-slate-900 rounded border border-slate-800 font-mono text-[10px] overflow-x-auto text-slate-300">
                    <div className="text-slate-400 mb-1">// Input Payload</div>
                    <pre>{JSON.stringify(log.input_payload, null, 2)}</pre>
                    <div className="text-slate-400 my-1">// Output Payload</div>
                    <pre>{JSON.stringify(log.output_payload, null, 2)}</pre>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
