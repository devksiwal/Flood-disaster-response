import { Incident, Team, FloodSensor, ReliefCamp, RescueRoute, FloodRiskZone, AgentLog } from '../types';

const API_BASE = '/api/v1';

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {})
  };

  try {
    const res = await fetch(url, { ...options, headers });
    if (!res.ok) {
      const errorBody = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(errorBody.detail || `Request failed with status ${res.status}`);
    }
    return await res.json();
  } catch (err: any) {
    console.error(`API Error on [${options.method || 'GET'} ${url}]:`, err);
    throw err;
  }
}

// Incidents
export const fetchIncidents = (status?: string, priority?: string) => {
  const params = new URLSearchParams();
  if (status) params.append('status', status);
  if (priority) params.append('priority', priority);
  const q = params.toString() ? `?${params.toString()}` : '';
  return request<Incident[]>(`/incidents${q}`);
};

export const fetchIncidentDetails = (id: string) => {
  return request<{ incident: Incident; assigned_team: Team | null; route: RescueRoute | null }>(`/incidents/${id}`);
};

export const submitSOS = (data: { raw_sos: string; caller_contact?: string; latitude?: number; longitude?: number; location_name?: string }) => {
  return request<{ status: string; incident_id: string; result: any }>('/incidents/sos', {
    method: 'POST',
    body: JSON.stringify(data)
  });
};

export const updateIncidentStatus = (id: string, status: string) => {
  return request<{ message: string }>(`/incidents/${id}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ status })
  });
};

// Teams
export const fetchTeams = () => request<Team[]>('/teams');

export const updateTeamStatus = (teamId: string, status: string) => {
  return request<{ message: string }>(`/teams/${teamId}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ status })
  });
};

// Flood Monitoring
export const fetchFloodSensors = () => request<FloodSensor[]>('/flood/sensors');
export const fetchFloodZones = () => request<FloodRiskZone[]>('/flood/zones');

export const updateSensorTelemetry = (sensorId: string, waterLevel: number, trend: string) => {
  return request<{ message: string; current_level: number; status: string }>(`/flood/sensor/${sensorId}/telemetry`, {
    method: 'POST',
    body: JSON.stringify({ water_level_meters: waterLevel, trend })
  });
};

// Relief Camps
export const fetchReliefCamps = () => request<ReliefCamp[]>('/camps');

export const admitCampEvacuees = (campId: string, admitCount: number, foodDelta: number = 0) => {
  return request<{ message: string; new_occupancy: number; available_beds: number; status: string }>(`/camps/${campId}/intake`, {
    method: 'PATCH',
    body: JSON.stringify({ admit_evacuees: admitCount, food_packets_delta: foodDelta })
  });
};

// Routes
export const fetchRescueRoutes = () => request<RescueRoute[]>('/routes');

// Agents
export const fetchAgentLogs = (incidentId?: string) => {
  const q = incidentId ? `?incident_id=${incidentId}` : '';
  return request<AgentLog[]>(`/agents/logs${q}`);
};

export const fetchAgentStatus = () => request<any>('/agents/status');

export const triggerAgentPipeline = (incidentId: string) => {
  return request<any>(`/agents/trigger/${incidentId}`, { method: 'POST' });
};
