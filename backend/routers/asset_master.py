"""Static Asset Master Library — predefined fire-safety equipment templates."""
from fastapi import APIRouter, Depends
from core.deps import get_current_user

router = APIRouter(prefix="/asset-master", tags=["asset-master"])

MASTER = [
    {"category": "extinguisher", "label": "Fire Extinguisher",
     "description": "Portable firefighting device. Use type-appropriate variant for the fire class.",
     "templates": [
        {"sub_type": "CO2 4.5kg", "description": "For electrical fires (Class C). Leaves no residue."},
        {"sub_type": "ABC 9kg", "description": "All-purpose dry powder for Class A/B/C."},
        {"sub_type": "Water 9L", "description": "Class A fires (wood, paper, textiles)."},
        {"sub_type": "Foam 9L", "description": "Class A & B fires — flammable liquids."},
        {"sub_type": "K-Class 6L", "description": "Kitchen fires — cooking oils & fats."},
     ]},
    {"category": "hydrant", "label": "Fire Hydrant",
     "description": "High-volume water-supply outlet for fire-fighting operations.",
     "templates": [
        {"sub_type": "Wet Riser", "description": "Charged vertical pipe internal to building."},
        {"sub_type": "Yard Hydrant", "description": "External hydrant with 63mm coupling."},
        {"sub_type": "Landing Valve", "description": "Hose connection point on each floor."},
     ]},
    {"category": "sprinkler", "label": "Sprinkler System",
     "description": "Automatic water-spray system triggered at elevated temperature.",
     "templates": [
        {"sub_type": "Upright", "description": "Spray pattern downward from ceiling level."},
        {"sub_type": "Pendant", "description": "Concealed ceiling-mounted, sprays downward."},
        {"sub_type": "Sidewall", "description": "Wall-mounted — covers across a room."},
     ]},
    {"category": "alarm", "label": "Alarm / Detector",
     "description": "Detection and audible-visual notification devices.",
     "templates": [
        {"sub_type": "Smoke Detector", "description": "Photoelectric / ionization smoke sensor."},
        {"sub_type": "Heat Detector", "description": "Rate-of-rise or fixed-temperature sensor."},
        {"sub_type": "Manual Call Point", "description": "Break-glass manual alarm trigger."},
        {"sub_type": "Fire Alarm Panel", "description": "Central control & annunciator for all detectors."},
     ]},
    {"category": "hose", "label": "Fire Hose",
     "description": "Flexible high-pressure water hose stored near hydrants.",
     "templates": [
        {"sub_type": "Fire Hose 30m", "description": "Standard 30m x 63mm canvas/rubber hose."},
        {"sub_type": "Hose Reel 30m", "description": "First-aid reel — 25mm continuous flow."},
     ]},
    {"category": "pump", "label": "Fire Pump",
     "description": "Pressurises the hydrant and sprinkler network.",
     "templates": [
        {"sub_type": "Main Electric Pump", "description": "Primary pump — 2280 LPM @ 7 bar typical."},
        {"sub_type": "Jockey Pump", "description": "Maintains standby pressure in the network."},
        {"sub_type": "Diesel Pump", "description": "Backup on mains failure."},
     ]},
    {"category": "other", "label": "Auxiliary Safety Equipment",
     "description": "Other life-safety equipment across the site.",
     "templates": [
        {"sub_type": "Emergency Light", "description": "Battery-backed exit-path lighting."},
        {"sub_type": "Fire Exit Sign", "description": "Photoluminescent route signage."},
        {"sub_type": "PA / Voice Alarm", "description": "Building-wide evacuation announcement."},
        {"sub_type": "Gas Suppression", "description": "FM-200 / CO2 / Novec — for data centres, LT rooms."},
     ]},
]


@router.get("")
async def list_master(user: dict = Depends(get_current_user)):
    return {"categories": MASTER}
