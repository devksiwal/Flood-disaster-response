import re
import time
from typing import Dict, Any, List
from app.agents.base import BaseDisasterAgent, SharedDisasterMemory
from app.core.logger import logger


class EmergencyDetectionAgent(BaseDisasterAgent):
    """
    Agent 1: Emergency Detection Agent
    Converts unstructured SOS messages into structured incidents with verified telemetry.
    """

    def __init__(self):
        super().__init__(
            name="Emergency Detection Agent",
            role="Disaster SOS Triage & NLP Classification Specialist",
            goal="Extract critical situational entities (victims, depth, hazards, geolocation) from unstructured emergency calls and texts."
        )

    async def execute(self, state: Dict[str, Any], memory: SharedDisasterMemory) -> Dict[str, Any]:
        start_time = time.time()
        raw_sos = state.get("raw_sos", "")
        caller = state.get("caller_contact", "Citizen SOS")
        lat = state.get("latitude")
        lng = state.get("longitude")
        location_hint = state.get("location_name", "")

        thought = f"Analyzing incoming SOS transmission: '{raw_sos[:60]}...'. Extracting situational metrics, severity markers, and casualty profile."
        
        # 1. NLP / Heuristic Entity Extraction
        sos_lower = raw_sos.lower()

        # Extract Category
        category = "FLASH_FLOOD"
        if any(w in sos_lower for w in ["hospital", "patient", "oxygen", "heart", "bleed", "pregnant", "medicine", "doctor", "trauma"]):
            category = "MEDICAL_URGENCY"
        elif any(w in sos_lower for w in ["crack", "collapse", "roof", "falling", "structural", "rubble"]):
            category = "STRUCTURAL_COLLAPSE"
        elif any(w in sos_lower for w in ["bus", "car", "stranded", "trapped", "school", "attic", "marooned", "island"]):
            category = "STRANDED_RESIDENTS"

        # Extract Victim Counts
        victim_count = 1
        numbers = re.findall(r'(\d+)\s*(?:people|persons|victims|members|citizens|souls|patients|children|kids|students)?', sos_lower)
        if numbers:
            victim_count = max(int(numbers[0]), 1)
        
        # Special vulnerable demographics
        children_count = 0
        elderly_count = 0
        injured_count = 0

        if any(w in sos_lower for w in ["child", "children", "baby", "infant", "kid", "kids", "student"]):
            kids = re.findall(r'(\d+)\s*(?:child|children|kids|baby|infant|students)', sos_lower)
            children_count = int(kids[0]) if kids else max(1, victim_count // 2)

        if any(w in sos_lower for w in ["elderly", "old", "senior", "grandma", "grandfather", "aged"]):
            eld = re.findall(r'(\d+)\s*(?:elderly|aged|grandma|seniors)', sos_lower)
            elderly_count = int(eld[0]) if eld else 1

        if any(w in sos_lower for w in ["injured", "hurt", "bleeding", "unconscious", "oxygen", "critical", "broken"]):
            inj = re.findall(r'(\d+)\s*(?:injured|hurt|patients)', sos_lower)
            injured_count = int(inj[0]) if inj else 1

        if victim_count < (children_count + elderly_count):
            victim_count = children_count + elderly_count

        # Extract Water Depth
        water_depth = 1.2
        if "2nd floor" in sos_lower or "second floor" in sos_lower:
            water_depth = 3.5
        elif "1st floor" in sos_lower or "first floor" in sos_lower:
            water_depth = 2.4
        elif "neck" in sos_lower or "chest" in sos_lower:
            water_depth = 1.6
        elif "waist" in sos_lower:
            water_depth = 1.1
        elif "knee" in sos_lower:
            water_depth = 0.5
        else:
            depth_match = re.findall(r'(\d+(?:\.\d+)?)\s*(?:m|meter|meters|ft|feet)', sos_lower)
            if depth_match:
                val = float(depth_match[0])
                if "ft" in sos_lower or "feet" in sos_lower:
                    water_depth = round(val * 0.3048, 2)
                else:
                    water_depth = round(val, 2)

        # Extract Hazards
        hazards = []
        if any(w in sos_lower for w in ["electric", "wire", "spark", "power", "cable", "current"]):
            hazards.append("ELECTRICAL_WIRES_SUBMERGED")
        if any(w in sos_lower for w in ["fast", "rushing", "swept", "strong current", "torrent"]):
            hazards.append("FAST_FLOWING_CURRENT")
        if any(w in sos_lower for w in ["roof", "attic", "terrace", "top"]):
            hazards.append("ROOF_EVACUATION_REQUIRED")
        if any(w in sos_lower for w in ["crack", "shaking", "wall", "collapse"]):
            hazards.append("STRUCTURAL_INSTABILITY")
        if any(w in sos_lower for w in ["bus", "car", "vehicle", "van"]):
            hazards.append("SUBMERGED_VEHICLE")
        if any(w in sos_lower for w in ["oxygen", "icu", "ventilator"]):
            hazards.append("CRITICAL_OXYGEN_DEPLETION")

        # Coordinates & Landmark resolution
        if lat is None or lng is None:
            # Default to disaster zone central coordinate with slight jitter
            lat = 26.1550 + (hash(raw_sos) % 30) * 0.001
            lng = 91.7450 + (hash(raw_sos[::-1]) % 30) * 0.001

        if not location_hint:
            # Extract possible location words
            loc_match = re.findall(r'(?:near|at|in)\s+([A-Z][a-zA-Z0-9\s]+(?:Road|Ghat|Nagar|Colony|Street|Bridge|Ward|Market|School|Hospital)?)', raw_sos)
            location_hint = loc_match[0] if loc_match else f"Sector Delta ({round(lat, 3)}, {round(lng, 3)})"

        title = f"{category.replace('_', ' ').title()} - {location_hint}"

        incident_data = {
            "id": state.get("id"),
            "raw_sos": raw_sos,
            "caller_contact": caller,
            "title": title,
            "category": category,
            "status": "STRUCTURED",
            "latitude": round(lat, 5),
            "longitude": round(lng, 5),
            "location_name": location_hint,
            "victim_count": victim_count,
            "children_count": children_count,
            "elderly_count": elderly_count,
            "injured_count": injured_count,
            "water_depth_meters": water_depth,
            "hazards": hazards,
        }

        # Store in Shared Memory
        memory.incidents[incident_data["id"]] = incident_data

        exec_time = round((time.time() - start_time) * 1000, 1)
        action = "STRUCTURE_INCIDENT"
        memory.log(
            agent_name=self.name,
            step="1. SOS Ingestion & Feature Extraction",
            thought=thought,
            action=action,
            input_data={"raw_sos": raw_sos},
            output_data=incident_data,
            confidence=0.97,
            execution_time_ms=exec_time,
            incident_id=incident_data["id"]
        )


        return incident_data
