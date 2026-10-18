from typing import Dict, Any
from datetime import datetime, timezone


def generate_citizen_sms(incident: Dict[str, Any], team: Dict[str, Any], eta_minutes: float) -> str:
    """Generate reassurance and safety SMS for caller/trapped citizens."""
    return (
        f"🚨 [NDMA RESCUE ALERT] Your SOS for {incident.get('location_name', 'your sector')} has been verified. "
        f"Rescue Team '{team.get('callsign')}' has been dispatched. Estimated Arrival: {eta_minutes} mins. "
        f"ACTION: Move to the highest accessible level or rooftop. Disconnect all electrical mains. "
        f"Wave bright cloth or flash phone light when team approaches. Stay calm, help is en route."
    )


def generate_team_dispatch_order(incident: Dict[str, Any], team: Dict[str, Any], route_summary: str) -> Dict[str, Any]:
    """Generate tactical dispatch order for field responder unit."""
    return {
        "order_id": f"ORD-{incident.get('id')}",
        "team_callsign": team.get("callsign"),
        "target_coordinates": [incident.get("latitude"), incident.get("longitude")],
        "location_name": incident.get("location_name"),
        "priority_level": incident.get("priority_level"),
        "victim_profile": {
            "total": incident.get("victim_count"),
            "children": incident.get("children_count", 0),
            "elderly": incident.get("elderly_count", 0),
            "injured": incident.get("injured_count", 0)
        },
        "water_depth": f"{incident.get('water_depth_meters', 1.0)}m",
        "hazards": incident.get("hazards", []),
        "route_instructions": route_summary,
        "radio_frequency": team.get("contact_radio", "VHF-CH-16"),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


def generate_deoc_sitrep(incident: Dict[str, Any], team: Dict[str, Any], camp: Dict[str, Any]) -> str:
    """Generate formal District Emergency Operations Center (DEOC) Situation Report."""
    return (
        f"*** SITUATION REPORT (SITREP) ***\n"
        f"Incident ID: {incident.get('id')} | Priority: {incident.get('priority_level')} ({incident.get('priority_score')}/100)\n"
        f"Location: {incident.get('location_name')} ({incident.get('latitude')}, {incident.get('longitude')})\n"
        f"Casualties / Trapped: {incident.get('victim_count')} individuals ({incident.get('elderly_count')} elderly, {incident.get('children_count')} children)\n"
        f"Dispatched Unit: {team.get('callsign')} (Boats: {team.get('boats_count')}, Amphibious: {team.get('amphibious_vehicles')})\n"
        f"Designated Safe Shelter: {camp.get('name')} (Available Beds: {camp.get('available_beds')})\n"
        f"Timestamp: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}"
    )


def generate_camp_intake_advisory(incident: Dict[str, Any], camp: Dict[str, Any]) -> str:
    """Alert camp logistics officer to prepare beds, food, and medical triage."""
    return (
        f"📋 [CAMP INTAKE ADVISORY] Attention {camp.get('contact_person')}: "
        f"Prepare intake for {incident.get('victim_count')} incoming evacuees from {incident.get('location_name')}. "
        f"Medical triage required for {incident.get('injured_count', 0)} injured victims. "
        f"Prepare {incident.get('victim_count')} dry ration packets and hydration kits."
    )
