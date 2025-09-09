from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import uuid
from datetime import datetime, timezone
from enum import Enum
import math

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Enums
class MaterialType(str, Enum):
    ALUMINUM = "aluminum"
    UPVC = "upvc"
    WOOD = "wood"
    STEEL = "steel"

class OpeningType(str, Enum):
    CASEMENT = "casement"  # Batiente
    AWNING = "awning"  # Proyectante
    TURN_TILT = "turn_tilt"  # Oscilobatiente
    SLIDING = "sliding"  # Corredera
    FOLDING = "folding"  # Plegable

class ProfileType(str, Enum):
    FRAME = "frame"
    SASH = "sash"
    MULLION = "mullion"
    TRANSOM = "transom"

# Pydantic Models
class MaterialSystem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    material_type: MaterialType
    compatible_openings: List[OpeningType]
    description: Optional[str] = None

class Profile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    system_id: str
    code: str
    profile_type: ProfileType
    bar_length: float  # mm
    weight_per_meter: float  # kg/m
    cost_per_meter: float  # currency/m
    description: Optional[str] = None

class Hardware(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    system: str
    name: str
    hardware_type: str  # hinge, handle, lock, etc.
    cost: float
    compatible_openings: List[OpeningType]
    max_weight: Optional[float] = None  # kg
    max_width: Optional[float] = None  # mm
    max_height: Optional[float] = None  # mm

class Glass(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    description: str
    thickness: float  # mm
    glass_type: str  # double, triple, laminated, etc.
    u_value: float  # W/m²K
    cost_per_m2: float

class WindowConfig(BaseModel):
    width: float  # mm
    height: float  # mm
    opening_type: OpeningType
    system_id: str
    glass_id: str
    leaves: int = 1
    mullions: int = 0
    transoms: int = 0

class BOMItem(BaseModel):
    item_id: str
    item_type: str  # profile, hardware, glass
    description: str
    quantity: float
    unit: str  # m, pcs, m2
    unit_cost: float
    total_cost: float

class WindowCalculation(BaseModel):
    config: WindowConfig
    bom_items: List[BOMItem]
    total_material_cost: float
    labor_cost: float
    margin_percent: float
    final_price: float
    weight: float  # kg
    glass_area: float  # m2

class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    currency: str = "USD"
    margin_percent: float = 30.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    items: List[Dict] = []

# Database initialization data
async def init_sample_data():
    # Check if data already exists
    existing_systems = await db.material_systems.count_documents({})
    if existing_systems > 0:
        return
    
    # Material Systems
    systems = [
        MaterialSystem(
            name="Alu-Serie 45",
            material_type=MaterialType.ALUMINUM,
            compatible_openings=[OpeningType.CASEMENT, OpeningType.AWNING, OpeningType.TURN_TILT],
            description="Sistema de aluminio de 45mm para uso residencial"
        ),
        MaterialSystem(
            name="uPVC-Serie 70",
            material_type=MaterialType.UPVC,
            compatible_openings=[OpeningType.CASEMENT, OpeningType.TURN_TILT, OpeningType.SLIDING],
            description="Sistema uPVC de 70mm con cámaras múltiples"
        ),
        MaterialSystem(
            name="Madera-Euro68",
            material_type=MaterialType.WOOD,
            compatible_openings=[OpeningType.CASEMENT, OpeningType.AWNING, OpeningType.TURN_TILT],
            description="Sistema de madera europea de 68mm"
        )
    ]
    
    for system in systems:
        await db.material_systems.insert_one(system.dict())
    
    # Get system IDs for profiles
    alu_system = await db.material_systems.find_one({"name": "Alu-Serie 45"})
    upvc_system = await db.material_systems.find_one({"name": "uPVC-Serie 70"})
    wood_system = await db.material_systems.find_one({"name": "Madera-Euro68"})
    
    # Profiles
    profiles = [
        # Aluminum profiles
        Profile(system_id=alu_system["id"], code="ALU-F45", profile_type=ProfileType.FRAME, 
                bar_length=6000, weight_per_meter=1.2, cost_per_meter=15.50, description="Marco aluminio 45mm"),
        Profile(system_id=alu_system["id"], code="ALU-S45", profile_type=ProfileType.SASH, 
                bar_length=6000, weight_per_meter=0.9, cost_per_meter=12.30, description="Hoja aluminio 45mm"),
        Profile(system_id=alu_system["id"], code="ALU-M45", profile_type=ProfileType.MULLION, 
                bar_length=6000, weight_per_meter=1.0, cost_per_meter=13.80, description="Travesaño aluminio 45mm"),
        
        # uPVC profiles
        Profile(system_id=upvc_system["id"], code="PVC-F70", profile_type=ProfileType.FRAME, 
                bar_length=6000, weight_per_meter=2.1, cost_per_meter=18.90, description="Marco uPVC 70mm"),
        Profile(system_id=upvc_system["id"], code="PVC-S70", profile_type=ProfileType.SASH, 
                bar_length=6000, weight_per_meter=1.8, cost_per_meter=16.70, description="Hoja uPVC 70mm"),
        
        # Wood profiles
        Profile(system_id=wood_system["id"], code="WOOD-F68", profile_type=ProfileType.FRAME, 
                bar_length=6000, weight_per_meter=2.8, cost_per_meter=35.50, description="Marco madera 68mm"),
        Profile(system_id=wood_system["id"], code="WOOD-S68", profile_type=ProfileType.SASH, 
                bar_length=6000, weight_per_meter=2.5, cost_per_meter=32.80, description="Hoja madera 68mm"),
    ]
    
    for profile in profiles:
        await db.profiles.insert_one(profile.dict())
    
    # Hardware
    hardware_items = [
        Hardware(system="universal", name="Kit Batiente Estándar", hardware_type="casement_kit", 
                cost=45.80, compatible_openings=[OpeningType.CASEMENT], max_weight=80, max_width=1200, max_height=1500),
        Hardware(system="universal", name="Kit Proyectante", hardware_type="awning_kit", 
                cost=38.50, compatible_openings=[OpeningType.AWNING], max_weight=60, max_width=1000, max_height=800),
        Hardware(system="universal", name="Kit Oscilobatiente", hardware_type="turn_tilt_kit", 
                cost=125.90, compatible_openings=[OpeningType.TURN_TILT], max_weight=100, max_width=1400, max_height=1800),
        Hardware(system="universal", name="Kit Corredera", hardware_type="sliding_kit", 
                cost=67.30, compatible_openings=[OpeningType.SLIDING], max_weight=120, max_width=2500, max_height=2200),
        Hardware(system="universal", name="Manilla Estándar", hardware_type="handle", 
                cost=18.90, compatible_openings=list(OpeningType)),
        Hardware(system="universal", name="Cerradura Multipunto", hardware_type="lock", 
                cost=89.50, compatible_openings=[OpeningType.CASEMENT, OpeningType.TURN_TILT]),
    ]
    
    for hardware in hardware_items:
        await db.hardware.insert_one(hardware.dict())
    
    # Glass types
    glass_types = [
        Glass(description="4-12-4 Doble Acrist.", thickness=20, glass_type="double", u_value=2.8, cost_per_m2=28.50),
        Glass(description="4-16-4 Doble Acrist.", thickness=24, glass_type="double", u_value=2.6, cost_per_m2=32.80),
        Glass(description="6-12-6 Doble Acrist.", thickness=24, glass_type="double", u_value=2.7, cost_per_m2=35.90),
        Glass(description="3+3 Laminado", thickness=6, glass_type="laminated", u_value=5.8, cost_per_m2=42.30),
        Glass(description="Triple 4-12-4-12-4", thickness=32, glass_type="triple", u_value=1.8, cost_per_m2=48.70),
    ]
    
    for glass in glass_types:
        await db.glass.insert_one(glass.dict())

# Calculation Engine
class WindowCalculator:
    @staticmethod
    def calculate_perimeter_profiles(config: WindowConfig) -> Dict[str, float]:
        """Calculate profile lengths needed based on window configuration"""
        width = config.width
        height = config.height
        leaves = config.leaves
        mullions = config.mullions
        transoms = config.transoms
        
        # Basic frame perimeter
        frame_perimeter = 2 * (width + height)
        
        # Sash calculation depends on opening type and leaves
        if config.opening_type == OpeningType.SLIDING:
            # Sliding windows: sash perimeter per leaf
            leaf_width = width / leaves
            sash_perimeter = leaves * 2 * (leaf_width + height)
        else:
            # Other types: standard sash calculation
            if leaves == 1:
                sash_perimeter = 2 * (width + height) * 0.9  # Single leaf
            else:
                leaf_width = width / leaves
                sash_perimeter = leaves * 2 * (leaf_width + height)
        
        # Mullions (vertical dividers)
        mullion_length = mullions * height
        
        # Transoms (horizontal dividers) 
        transom_length = transoms * width
        
        return {
            "frame": frame_perimeter,
            "sash": sash_perimeter,
            "mullion": mullion_length,
            "transom": transom_length
        }
    
    @staticmethod
    def calculate_glass_area(config: WindowConfig) -> float:
        """Calculate glass area accounting for frame dimensions"""
        # Assume 80mm frame reduction total (40mm per side)
        glass_width = max(0, config.width - 80)
        glass_height = max(0, config.height - 80)
        
        # For multiple leaves, reduce width per leaf
        if config.leaves > 1:
            glass_width = glass_width / config.leaves
            return (glass_width * glass_height * config.leaves) / 1000000  # mm² to m²
        
        return (glass_width * glass_height) / 1000000  # mm² to m²
    
    @staticmethod
    def calculate_weight(config: WindowConfig, profiles: List[Dict], glass: Dict) -> float:
        """Calculate total window weight"""
        perimeters = WindowCalculator.calculate_perimeter_profiles(config)
        weight = 0
        
        # Profile weights
        for profile in profiles:
            if profile["profile_type"] in perimeters:
                length_m = perimeters[profile["profile_type"]] / 1000
                weight += length_m * profile["weight_per_meter"]
        
        # Glass weight (approx 2.5 kg/m² per mm thickness)
        glass_area = WindowCalculator.calculate_glass_area(config)
        glass_weight = glass_area * glass["thickness"] * 2.5
        weight += glass_weight
        
        return weight

# API Routes

@api_router.get("/material-systems", response_model=List[MaterialSystem])
async def get_material_systems():
    systems = await db.material_systems.find().to_list(1000)
    return [MaterialSystem(**system) for system in systems]

@api_router.get("/profiles/{system_id}")
async def get_profiles_by_system(system_id: str):
    profiles = await db.profiles.find({"system_id": system_id}).to_list(1000)
    return profiles

@api_router.get("/hardware", response_model=List[Hardware])
async def get_hardware():
    hardware = await db.hardware.find().to_list(1000)
    return [Hardware(**hw) for hw in hardware]

@api_router.get("/glass", response_model=List[Glass])
async def get_glass_types():
    glass_types = await db.glass.find().to_list(1000)
    return [Glass(**glass) for glass in glass_types]

@api_router.post("/calculate", response_model=WindowCalculation)
async def calculate_window(config: WindowConfig):
    try:
        # Get system profiles
        profiles = await db.profiles.find({"system_id": config.system_id}).to_list(1000)
        if not profiles:
            raise HTTPException(status_code=404, detail="No profiles found for system")
        
        # Get glass
        glass = await db.glass.find_one({"id": config.glass_id})
        if not glass:
            raise HTTPException(status_code=404, detail="Glass type not found")
        
        # Get compatible hardware
        hardware = await db.hardware.find({
            "compatible_openings": config.opening_type
        }).to_list(1000)
        
        # Calculate profile lengths needed
        perimeters = WindowCalculator.calculate_perimeter_profiles(config)
        
        # Build BOM
        bom_items = []
        total_material_cost = 0
        
        # Add profiles to BOM
        for profile in profiles:
            profile_type = profile["profile_type"]
            if profile_type in perimeters and perimeters[profile_type] > 0:
                length_m = perimeters[profile_type] / 1000  # mm to m
                cost = length_m * profile["cost_per_meter"]
                
                bom_items.append(BOMItem(
                    item_id=profile["id"],
                    item_type="profile",
                    description=f"{profile['description']} - {profile['code']}",
                    quantity=length_m,
                    unit="m",
                    unit_cost=profile["cost_per_meter"],
                    total_cost=cost
                ))
                total_material_cost += cost
        
        # Add glass to BOM
        glass_area = WindowCalculator.calculate_glass_area(config)
        glass_cost = glass_area * glass["cost_per_m2"]
        
        bom_items.append(BOMItem(
            item_id=glass["id"],
            item_type="glass",
            description=glass["description"],
            quantity=glass_area,
            unit="m²",
            unit_cost=glass["cost_per_m2"],
            total_cost=glass_cost
        ))
        total_material_cost += glass_cost
        
        # Add compatible hardware
        for hw in hardware:
            # Filter hardware based on window dimensions and weight
            window_weight = WindowCalculator.calculate_weight(config, profiles, glass)
            
            if (not hw.get("max_width") or config.width <= hw["max_width"]) and \
               (not hw.get("max_height") or config.height <= hw["max_height"]) and \
               (not hw.get("max_weight") or window_weight <= hw["max_weight"]):
                
                bom_items.append(BOMItem(
                    item_id=hw["id"],
                    item_type="hardware",
                    description=hw["name"],
                    quantity=1,
                    unit="pcs",
                    unit_cost=hw["cost"],
                    total_cost=hw["cost"]
                ))
                total_material_cost += hw["cost"]
        
        # Calculate labor cost (10% of material cost)
        labor_cost = total_material_cost * 0.10
        
        # Calculate final price with margin
        margin_percent = 30.0  # Default margin
        subtotal = total_material_cost + labor_cost
        final_price = subtotal * (1 + margin_percent / 100)
        
        # Calculate weight
        weight = WindowCalculator.calculate_weight(config, profiles, glass)
        
        return WindowCalculation(
            config=config,
            bom_items=bom_items,
            total_material_cost=total_material_cost,
            labor_cost=labor_cost,
            margin_percent=margin_percent,
            final_price=final_price,
            weight=weight,
            glass_area=glass_area
        )
        
    except Exception as e:
        logger.error(f"Calculation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")

@api_router.post("/projects", response_model=Project)
async def create_project(project: Project):
    project_dict = project.dict()
    await db.projects.insert_one(project_dict)
    return project

@api_router.get("/projects", response_model=List[Project])
async def get_projects():
    projects = await db.projects.find().to_list(1000)
    return [Project(**project) for project in projects]

@api_router.get("/init-data")
async def initialize_data():
    await init_sample_data()
    return {"message": "Sample data initialized successfully"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()