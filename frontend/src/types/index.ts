export interface Incident {
  id: string;
  title: string;
  raw_sos: string;
  category: 'FLASH_FLOOD' | 'STRANDED_RESIDENTS' | 'STRUCTURAL_COLLAPSE' | 'MEDICAL_URGENCY';
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  priority_score: number;
  priority_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  status: 'REPORTED' | 'TRIAGED' | 'DISPATCHED' | 'IN_PROGRESS' | 'RESCUED' | 'RESOLVED';
  latitude: number;
  longitude: number;
  location_name: string;
  victim_count: number;
  children_count: number;
  elderly_count: number;
  injured_count: number;
  water_depth_meters: number;
  hazards: string[];
  assigned_team_id?: string | null;
  assigned_camp_id?: string | null;
  created_at?: string;
}

export interface Team {
  id: string;
  callsign: string;
  agency: 'NDRF' | 'SDRF' | 'COAST_GUARD' | 'MEDICAL_CORPS' | 'DRONE_RECON' | 'CIVIL_DEFENSE';
  status: 'AVAILABLE' | 'DISPATCHED' | 'ON_MISSION' | 'RETURNING';
  latitude: number;
  longitude: number;
  base_station: string;
  personnel_count: number;
  boats_count: number;
  medical_kits: number;
  drones_count: number;
  amphibious_vehicles: number;
  contact_radio: string;
  current_incident_id?: string | null;
  updated_at?: string;
}

export interface FloodSensor {
  id: string;
  station_code: string;
  station_name: string;
  river_basin: string;
  latitude: number;
  longitude: number;
  water_level_meters: number;
  danger_mark_meters: number;
  warning_level_meters: number;
  trend: 'RISING' | 'STEADY' | 'RECEDING';
  rainfall_mm_last_3h: number;
  discharge_cusecs: number;
  status: 'NORMAL' | 'WARNING' | 'CRITICAL';
  last_ping?: string;
}

export interface ReliefCamp {
  id: string;
  name: string;
  location_name: string;
  latitude: number;
  longitude: number;
  total_capacity: number;
  current_occupancy: number;
  available_beds: number;
  occupancy_rate_percent: number;
  food_packets: number;
  drinking_water_liters: number;
  doctors_on_site: number;
  status: 'OPEN' | 'FULL' | 'STANDBY';
  contact_person: string;
  phone: string;
}

export interface RescueRoute {
  id: string;
  incident_id: string;
  team_id: string;
  camp_id?: string | null;
  waypoints: [number, number][];
  distance_km: number;
  estimated_minutes: number;
  flood_risk_level: string;
  route_summary: string;
  status: string;
  created_at?: string;
}

export interface FloodRiskZone {
  id: string;
  name: string;
  risk_level: 'EXTREME' | 'HIGH' | 'MODERATE' | 'SAFE';
  avg_depth_meters: number;
  current_speed_knots: number;
  is_navigable_by_boat: boolean;
  polygon: [number, number][];
}

export interface AgentLog {
  id: number;
  incident_id?: string;
  agent_name: string;
  step: string;
  thought: string;
  action: string;
  input_payload: any;
  output_payload: any;
  confidence: number;
  execution_time_ms: number;
  created_at?: string;
}

export interface WSEvent {
  id: string;
  type: string;
  data: any;
  timestamp: string;
}
