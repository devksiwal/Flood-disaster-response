import React, { useState, useEffect, useCallback } from 'react';
import { Navbar } from './components/Navbar';
import { LiveMap } from './components/LiveMap';
import { AgentTerminal } from './components/AgentTerminal';
import { IncidentBoard } from './components/IncidentBoard';
import { TeamDispatch } from './components/TeamDispatch';
import { ReliefCampTracker } from './components/ReliefCampTracker';
import { FloodAnalytics } from './components/FloodAnalytics';
import { SOSModal } from './components/SOSModal';
import { CitizenPortal } from './components/CitizenPortal';
import {
  fetchIncidents,
  fetchTeams,
  fetchFloodSensors,
  fetchFloodZones,
  fetchReliefCamps,
  fetchRescueRoutes,
  fetchAgentLogs,
  submitSOS,
  updateIncidentStatus,
  updateTeamStatus,
  admitCampEvacuees,
  updateSensorTelemetry,
  triggerAgentPipeline,
} from './services/api';
import { wsClient } from './services/websocket';
import { Incident, Team, FloodSensor, ReliefCamp, RescueRoute, FloodRiskZone, AgentLog, WSEvent } from './types';
import {
  AlertCircle,
  Shield,
  Waves,
  Home,
  Map as MapIcon,
  Terminal,
} from 'lucide-react';

type TabKey = 'INCIDENTS' | 'TEAMS' | 'CAMPS' | 'HYDROLOGY' | 'MAP' | 'AGENTS';

export const App: React.FC = () => {
  // --------------- State ---------------
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [teams, setTeams] = useState<Team[]>([]);
  const [sensors, setSensors] = useState<FloodSensor[]>([]);
  const [camps, setCamps] = useState<ReliefCamp[]>([]);
  const [routes, setRoutes] = useState<RescueRoute[]>([]);
  const [zones, setZones] = useState<FloodRiskZone[]>([]);
  const [agentLogs, setAgentLogs] = useState<AgentLog[]>([]);
  const [isPipelineRunning, setIsPipelineRunning] = useState(false);
  const [isSOSModalOpen, setIsSOSModalOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<TabKey>('INCIDENTS');
  const [selectedIncidentId, setSelectedIncidentId] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'EOC' | 'CITIZEN'>('EOC');
  const [lastSubmittedIncidentId, setLastSubmittedIncidentId] = useState<string | null>(null);

  // --------------- Data loading ---------------
  const loadDashboardData = useCallback(async () => {
    try {
      const [incRes, teamsRes, sensorsRes, campsRes, routesRes, zonesRes, logsRes] =
        await Promise.allSettled([
          fetchIncidents(),
          fetchTeams(),
          fetchFloodSensors(),
          fetchReliefCamps(),
          fetchRescueRoutes(),
          fetchFloodZones(),
          fetchAgentLogs(),
        ]);
      if (incRes.status === 'fulfilled') setIncidents(incRes.value);
      if (teamsRes.status === 'fulfilled') setTeams(teamsRes.value);
      if (sensorsRes.status === 'fulfilled') setSensors(sensorsRes.value);
      if (campsRes.status === 'fulfilled') setCamps(campsRes.value);
      if (routesRes.status === 'fulfilled') setRoutes(routesRes.value);
      if (zonesRes.status === 'fulfilled') setZones(zonesRes.value);
      if (logsRes.status === 'fulfilled') setAgentLogs(logsRes.value);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    }
  }, []);

  useEffect(() => {
    loadDashboardData();

    wsClient.connect();
    const unsubscribe = wsClient.subscribe((event: WSEvent) => {
      if (event.type === 'PIPELINE_STARTED') {
        setIsPipelineRunning(true);
      } else if (event.type === 'AGENT_STEP_COMPLETED') {
        const d = event.data;
        const newLog: AgentLog = {
          id: Date.now() + Math.random(),
          incident_id: d.incident_id || d.details?.incident_id,
          agent_name: d.agent_name || d.agent,
          step: d.step,
          thought: d.thought,
          action: d.action,
          input_payload: d.input_data,
          output_payload: d.output_data,
          confidence: d.confidence || 0.96,
          execution_time_ms: d.execution_time_ms || 110,
          created_at: d.timestamp,
        };
        setAgentLogs((prev) => [newLog, ...prev]);
      } else if (event.type === 'PIPELINE_COMPLETED') {
        setIsPipelineRunning(false);
        loadDashboardData();
      } else if (
        ['SENSOR_TELEMETRY_UPDATED', 'CAMP_OCCUPANCY_CHANGED', 'TEAM_STATUS_CHANGED', 'INCIDENT_STATUS_CHANGED'].includes(event.type)
      ) {
        loadDashboardData();
      }
    });

    return () => {
      unsubscribe();
    };
  }, [loadDashboardData]);

  // --------------- Handlers ---------------
  const handleSOSSubmit = async (data: { raw_sos: string; caller_contact?: string; location_name?: string; latitude?: number; longitude?: number }) => {
    const response = await submitSOS(data);
    setLastSubmittedIncidentId(response.incident_id);
    setIsSOSModalOpen(false);
    await loadDashboardData();
  };

  const handleTriggerPipeline = async (incidentId: string) => {
    await triggerAgentPipeline(incidentId);
  };

  const handleUpdateIncidentStatus = async (id: string, status: string) => {
    await updateIncidentStatus(id, status);
    loadDashboardData();
  };

  const handleUpdateTeamStatus = async (teamId: string, status: string) => {
    await updateTeamStatus(teamId, status);
    loadDashboardData();
  };

  const handleAdmitEvacuees = async (campId: string, count: number) => {
    await admitCampEvacuees(campId, count);
    loadDashboardData();
  };

  const handleSimulateSensorSurge = async (sensorId: string, currentLevel: number) => {
    await updateSensorTelemetry(sensorId, currentLevel + 1.5, 'RISING');
    loadDashboardData();
  };

  // --------------- Derived KPIs ---------------
  const criticalIncidentsCount = incidents.filter((i) => i.priority_level === 'CRITICAL').length;
  const dispatchedTeamsCount = teams.filter((t) => t.status === 'DISPATCHED' || t.status === 'ON_MISSION').length;
  const criticalSensorsCount = sensors.filter((s) => s.status === 'CRITICAL').length;
  const totalEvacuees = camps.reduce((acc, c) => acc + c.current_occupancy, 0);

  // --------------- Tab config ---------------
  const tabs: { key: TabKey; label: string; icon: React.ReactNode; count?: number | string }[] = [
    { key: 'INCIDENTS', label: 'Incidents', icon: <AlertCircle className="w-3.5 h-3.5" />, count: incidents.length },
    { key: 'TEAMS', label: 'Rescue Teams', icon: <Shield className="w-3.5 h-3.5" />, count: teams.length },
    { key: 'CAMPS', label: 'Relief Camps', icon: <Home className="w-3.5 h-3.5" />, count: camps.length },
    { key: 'HYDROLOGY', label: 'River Sensors', icon: <Waves className="w-3.5 h-3.5" />, count: sensors.length },
    { key: 'MAP', label: 'Live Map', icon: <MapIcon className="w-3.5 h-3.5" /> },
    { key: 'AGENTS', label: 'AI Agents', icon: <Terminal className="w-3.5 h-3.5" />, count: '6' },
  ];

  // --------------- Render ---------------
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      {/* Top Navbar */}
      <Navbar
        onOpenSOSModal={() => setIsSOSModalOpen(true)}
        activeIncidentCount={incidents.length}
        deployedTeamsCount={dispatchedTeamsCount}
        criticalSensorsCount={criticalSensorsCount}
        viewMode={viewMode}
        onToggleViewMode={() => setViewMode(viewMode === 'EOC' ? 'CITIZEN' : 'EOC')}
      />

      {viewMode === 'CITIZEN' ? (
        <CitizenPortal
          onBackToEOC={() => setViewMode('EOC')}
          onSubmitSOS={handleSOSSubmit}
          incidents={incidents}
          teams={teams}
          camps={camps}
          lastSubmittedIncidentId={lastSubmittedIncidentId}
        />
      ) : (
        <>
      <main className="flex-1 max-w-[1920px] w-full mx-auto p-4 space-y-4">
        {/* ─── KPI Summary Strip ─── */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <KpiCard label="Distress Incidents" value={incidents.length} sub={`${criticalIncidentsCount} critical`} subColor="text-red-400" icon={<AlertCircle className="w-4 h-4" />} />
          <KpiCard label="Deployed Teams" value={dispatchedTeamsCount} sub={`/ ${teams.length} units`} icon={<Shield className="w-4 h-4" />} />
          <KpiCard label="Sheltered Evacuees" value={totalEvacuees} sub={`${camps.length} camps`} icon={<Home className="w-4 h-4" />} />
          <KpiCard label="River Threat" value={criticalSensorsCount > 0 ? `${criticalSensorsCount} DANGER` : 'WATCH'} sub={`${sensors.length} stations`} icon={<Waves className="w-4 h-4" />} />
        </div>

        {/* ─── Tab Navigation ─── */}
        <div className="border-b border-slate-800">
          <div className="flex items-center gap-1 overflow-x-auto">
            {tabs.map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={`flex items-center gap-1.5 px-3 py-2 text-xs font-medium border-b-2 transition-colors whitespace-nowrap ${
                  activeTab === tab.key
                    ? 'border-slate-300 text-slate-100 bg-slate-900'
                    : 'border-transparent text-slate-500 hover:text-slate-300'
                }`}
              >
                {tab.icon}
                <span>{tab.label}</span>
                {tab.count !== undefined && (
                  <span className="text-[10px] bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded">{tab.count}</span>
                )}
              </button>
            ))}
          </div>
        </div>

        {/* ─── Tab Panels ─── */}
        <div className="min-h-[500px]">
          {activeTab === 'INCIDENTS' && (
            <IncidentBoard
              incidents={incidents}
              selectedIncidentId={selectedIncidentId}
              onSelectIncident={(id) => setSelectedIncidentId(id)}
              onTriggerPipeline={handleTriggerPipeline}
              onUpdateStatus={handleUpdateIncidentStatus}
            />
          )}

          {activeTab === 'TEAMS' && (
            <TeamDispatch teams={teams} onUpdateTeamStatus={handleUpdateTeamStatus} />
          )}

          {activeTab === 'CAMPS' && (
            <ReliefCampTracker camps={camps} onAdmitEvacuees={handleAdmitEvacuees} />
          )}

          {activeTab === 'HYDROLOGY' && (
            <FloodAnalytics sensors={sensors} onSimulateRise={handleSimulateSensorSurge} />
          )}

          {activeTab === 'MAP' && (
            <LiveMap
              incidents={incidents}
              teams={teams}
              sensors={sensors}
              camps={camps}
              routes={routes}
              zones={zones}
              selectedIncidentId={selectedIncidentId}
              onSelectIncident={(id) => setSelectedIncidentId(id)}
            />
          )}

          {activeTab === 'AGENTS' && (
            <AgentTerminal logs={agentLogs} isPipelineRunning={isPipelineRunning} />
          )}
        </div>
      </main>

      {/* Emergency SOS Modal */}
      <SOSModal
        isOpen={isSOSModalOpen}
        onClose={() => setIsSOSModalOpen(false)}
        onSubmit={handleSOSSubmit}
      />
        </>
      )}
    </div>
  );
};

// --------------- Minimal KPI Card ---------------
function KpiCard({
  label,
  value,
  sub,
  subColor = 'text-slate-500',
  icon,
}: {
  label: string;
  value: string | number;
  sub: string;
  subColor?: string;
  icon: React.ReactNode;
}) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg p-3 flex items-center justify-between">
      <div>
        <span className="text-[11px] font-medium text-slate-400">{label}</span>
        <div className="flex items-baseline gap-1.5 mt-0.5">
          <span className="text-xl font-bold font-mono text-slate-100">{value}</span>
          <span className={`text-xs ${subColor}`}>{sub}</span>
        </div>
      </div>
      <div className="w-8 h-8 rounded bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-400">
        {icon}
      </div>
    </div>
  );
}

export default App;
