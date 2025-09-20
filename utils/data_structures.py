"""
Data Structures for Bridge Design Application
Defines common data structures used across all modules
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union, Tuple
from enum import Enum
import numpy as np
import pandas as pd
from datetime import datetime

# Enumerations for standardized values
class BridgeType(Enum):
    SUBMERSIBLE = "Submersible Bridge"
    HIGH_LEVEL = "High Level Bridge"
    AQUEDUCT = "Aqueduct"
    CULVERT = "Culvert"
    VIADUCT = "Viaduct"

class LoadClass(Enum):
    CLASS_A = "Class A"
    CLASS_AA = "Class AA"
    CLASS_70R = "Class 70R"
    CLASS_A_70R = "Class A + 70R"

class DesignCode(Enum):
    IRC_6 = "IRC-6"
    IRC_21 = "IRC-21"
    IRC_112 = "IRC-112"
    IS_456 = "IS-456"
    IS_1893 = "IS-1893"

class ConcreteGrade(Enum):
    M20 = "M20"
    M25 = "M25"
    M30 = "M30"
    M35 = "M35"
    M40 = "M40"
    M45 = "M45"
    M50 = "M50"

class SteelGrade(Enum):
    Fe415 = "Fe415"
    Fe500 = "Fe500"
    Fe550 = "Fe550"
    Fe600 = "Fe600"

class AbutmentType(Enum):
    GRAVITY = "Gravity Type"
    CANTILEVER = "Cantilever Type"
    COUNTERFORT = "Counterfort Type"
    BUTTRESS = "Buttress Type"

class FoundationType(Enum):
    SHALLOW = "Shallow Foundation"
    DEEP = "Deep Foundation"
    PILE = "Pile Foundation"
    WELL = "Well Foundation"

# Basic data structures
@dataclass
class MaterialProperties:
    """Material properties for bridge design"""
    concrete_grade: ConcreteGrade = ConcreteGrade.M25
    steel_grade: SteelGrade = SteelGrade.Fe415
    concrete_density: float = 25.0  # kN/m³
    steel_density: float = 78.5     # kN/m³
    concrete_strength: float = 25.0  # N/mm²
    steel_yield_strength: float = 415.0  # N/mm²
    concrete_modulus: float = 25000.0  # N/mm²
    steel_modulus: float = 200000.0    # N/mm²
    poisson_ratio_concrete: float = 0.2
    poisson_ratio_steel: float = 0.3
    thermal_expansion_concrete: float = 12e-6  # per °C
    thermal_expansion_steel: float = 12e-6     # per °C

@dataclass
class SoilProperties:
    """Soil properties for foundation design"""
    soil_type: str = "Medium Dense Sand"
    unit_weight: float = 18.0        # kN/m³
    angle_of_friction: float = 30.0  # degrees
    cohesion: float = 0.0            # kN/m²
    bearing_capacity: float = 450.0  # kN/m²
    coefficient_of_friction: float = 0.5
    modulus_of_subgrade_reaction: float = 50000.0  # kN/m³
    water_table_depth: float = 5.0   # m below ground
    liquefaction_potential: str = "Low"

@dataclass
class HydraulicParameters:
    """Hydraulic design parameters"""
    design_discharge: float = 1000.0  # cumecs
    high_flood_level: float = 101.0   # m
    low_water_level: float = 95.0     # m
    normal_water_level: float = 98.0  # m
    bed_slope: str = "1 in 1000"
    manning_roughness: float = 0.033
    silt_factor: float = 1.5          # Lacey's silt factor
    regime_width: Optional[float] = None
    regime_depth: Optional[float] = None
    regime_velocity: Optional[float] = None
    calculated_afflux: Optional[float] = None
    design_scour_depth: Optional[float] = None

@dataclass
class LoadData:
    """Load data for structural analysis"""
    dead_load: float = 0.0           # kN/m or kN/m²
    live_load: float = 0.0           # kN/m or kN/m²
    wind_load: float = 0.0           # kN/m or kN/m²
    seismic_load: float = 0.0        # kN/m or kN/m²
    temperature_load: float = 0.0    # kN/m or kN/m²
    impact_factor: float = 0.25      # Impact factor
    load_class: LoadClass = LoadClass.CLASS_A
    load_factors: Dict[str, float] = field(default_factory=lambda: {
        'dead': 1.35,
        'live': 1.75,
        'wind': 1.50,
        'seismic': 1.50,
        'temperature': 1.20
    })

@dataclass
class GeometricData:
    """Geometric data for bridge elements"""
    length: float = 0.0              # m
    width: float = 0.0               # m
    height: float = 0.0              # m
    thickness: float = 0.0           # m
    span_length: float = 0.0         # m
    number_of_spans: int = 1
    skew_angle: float = 0.0          # degrees
    camber: float = 0.0              # m
    cross_slope: float = 2.5         # %

@dataclass
class BridgeConfiguration:
    """Complete bridge configuration"""
    bridge_name: str = "Bridge Project"
    location: str = "Project Location"
    project_type: str = BridgeType.HIGH_LEVEL.value
    bridge_type: BridgeType = BridgeType.HIGH_LEVEL
    span_length: float = 10.0        # m
    bridge_width: float = 7.5        # m
    carriageway_width: float = 7.5   # m
    footpath_width: float = 1.0      # m each side
    num_spans: int = 1
    skew_angle: float = 0.0          # degrees
    design_code: str = DesignCode.IRC_112.value
    concrete_grade: str = ConcreteGrade.M25.value
    steel_grade: str = SteelGrade.Fe415.value
    design_life: int = 100           # years
    load_class: str = LoadClass.CLASS_A.value
    
    # Additional configuration
    creation_date: datetime = field(default_factory=datetime.now)
    designed_by: str = "Bridge Engineer"
    checked_by: str = "Senior Engineer"
    approved_by: str = "Chief Engineer"
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        if self.span_length <= 0:
            raise ValueError("Span length must be positive")
        if self.bridge_width <= 0:
            raise ValueError("Bridge width must be positive")
        if not 0 <= self.skew_angle <= 60:
            raise ValueError("Skew angle must be between 0 and 60 degrees")

@dataclass
class DesignForces:
    """Design forces for structural elements"""
    axial_force: float = 0.0         # kN
    shear_force: float = 0.0         # kN
    bending_moment: float = 0.0      # kN-m
    torsional_moment: float = 0.0    # kN-m
    
    # Location where these forces act
    location_x: float = 0.0          # m
    location_y: float = 0.0          # m
    location_z: float = 0.0          # m
    
    # Load combination that produced these forces
    load_combination: str = "1.35DL + 1.75LL"
    
    # Factor of safety
    factor_of_safety: float = 1.0

@dataclass
class ReinforcementDetails:
    """Reinforcement details for concrete elements"""
    main_steel_area: float = 0.0     # mm²
    distribution_steel_area: float = 0.0  # mm²
    shear_steel_area: float = 0.0    # mm²
    
    # Bar details
    main_bar_diameter: int = 16      # mm
    main_bar_spacing: int = 200      # mm
    distribution_bar_diameter: int = 12  # mm
    distribution_bar_spacing: int = 250  # mm
    stirrup_diameter: int = 8        # mm
    stirrup_spacing: int = 200       # mm
    
    # Cover and development length
    clear_cover: int = 50            # mm
    development_length: int = 600    # mm
    lap_length: int = 800            # mm
    
    # Steel ratio
    steel_percentage: float = 0.0    # %
    
    def calculate_steel_percentage(self, concrete_area: float) -> float:
        """Calculate steel percentage"""
        if concrete_area > 0:
            self.steel_percentage = (self.main_steel_area / concrete_area) * 100
        return self.steel_percentage

@dataclass
class AnalysisResults:
    """Results from structural analysis"""
    analysis_type: str = "Unknown"
    status: str = "PENDING"          # PASS, FAIL, WARNING
    max_stress: float = 0.0          # N/mm²
    max_deflection: float = 0.0      # mm
    max_moment: float = 0.0          # kN-m
    max_shear: float = 0.0           # kN
    
    # Safety checks
    stress_ratio: float = 0.0        # Actual/Allowable
    deflection_ratio: float = 0.0    # Actual/Allowable
    safety_factor: float = 0.0
    
    # Detailed results
    detailed_results: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    
    # Analysis metadata
    analysis_date: datetime = field(default_factory=datetime.now)
    software_used: str = "Bridge Design Application"
    analyst: str = "System"

@dataclass
class StabilityResults:
    """Results from stability analysis"""
    overturning_factor: float = 0.0
    sliding_factor: float = 0.0
    bearing_pressure_max: float = 0.0  # kN/m²
    bearing_pressure_min: float = 0.0  # kN/m²
    eccentricity: float = 0.0          # m
    
    # Status of each check
    overturning_status: str = "PENDING"
    sliding_status: str = "PENDING"
    bearing_status: str = "PENDING"
    overall_status: str = "PENDING"
    
    # Forces
    total_vertical_force: float = 0.0   # kN
    total_horizontal_force: float = 0.0 # kN
    overturning_moment: float = 0.0     # kN-m
    resisting_moment: float = 0.0       # kN-m
    
    # Recommendations
    stability_recommendations: List[str] = field(default_factory=list)

@dataclass
class HydraulicResults:
    """Results from hydraulic analysis"""
    regime_width: float = 0.0        # m
    regime_depth: float = 0.0        # m
    regime_velocity: float = 0.0     # m/s
    calculated_afflux: float = 0.0   # m
    allowable_afflux: float = 0.3    # m
    scour_depth: float = 0.0         # m
    
    # Waterway adequacy
    required_waterway: float = 0.0   # m
    provided_waterway: float = 0.0   # m
    waterway_ratio: float = 0.0
    
    # Flow characteristics
    approach_velocity: float = 0.0   # m/s
    bridge_velocity: float = 0.0     # m/s
    velocity_ratio: float = 0.0
    
    # Status
    hydraulic_status: str = "PENDING"
    waterway_adequacy: str = "PENDING"
    afflux_status: str = "PENDING"
    
    # Recommendations
    hydraulic_recommendations: List[str] = field(default_factory=list)

@dataclass
class ProjectData:
    """Complete project data structure"""
    configuration: BridgeConfiguration
    materials: MaterialProperties
    soil: SoilProperties
    hydraulics: HydraulicParameters
    loads: LoadData
    geometry: GeometricData
    
    # Analysis results
    structural_results: Optional[AnalysisResults] = None
    stability_results: Optional[StabilityResults] = None
    hydraulic_results: Optional[HydraulicResults] = None
    
    # Design outputs
    reinforcement: Optional[ReinforcementDetails] = None
    design_forces: Optional[DesignForces] = None
    
    # Project metadata
    project_id: str = field(default_factory=lambda: f"PROJ_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    version: str = "1.0"
    last_modified: datetime = field(default_factory=datetime.now)
    
    def update_last_modified(self):
        """Update last modified timestamp"""
        self.last_modified = datetime.now()
    
    def get_project_summary(self) -> Dict[str, Any]:
        """Get summary of project data"""
        return {
            'project_id': self.project_id,
            'bridge_name': self.configuration.bridge_name,
            'location': self.configuration.location,
            'bridge_type': self.configuration.bridge_type.value,
            'span_length': self.configuration.span_length,
            'bridge_width': self.configuration.bridge_width,
            'design_code': self.configuration.design_code,
            'concrete_grade': self.configuration.concrete_grade,
            'steel_grade': self.configuration.steel_grade,
            'last_modified': self.last_modified.isoformat(),
            'version': self.version
        }

@dataclass
class ExcelFormulaData:
    """Data structure for Excel formula information"""
    cell_address: str
    formula: str
    sheet_name: str
    value: Any = None
    referenced_cells: List[str] = field(default_factory=list)
    referenced_ranges: List[str] = field(default_factory=list)
    excel_functions: List[str] = field(default_factory=list)
    formula_type: str = "unknown"
    complexity_score: int = 0
    
    # Engineering context
    engineering_category: str = "general"
    engineering_description: str = ""
    units: str = ""
    
    # Validation
    is_valid: bool = True
    validation_errors: List[str] = field(default_factory=list)
    
    def add_validation_error(self, error: str):
        """Add a validation error"""
        self.validation_errors.append(error)
        self.is_valid = False

@dataclass
class ClaudeValidationResult:
    """Results from Claude AI validation"""
    validation_id: str = field(default_factory=lambda: f"VAL_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    analysis_type: str = "Unknown"
    validation_type: str = "Formula Verification"
    
    # Overall assessment
    overall_status: str = "PENDING"  # ACCEPTABLE, NEEDS_REVIEW, CRITICAL_ISSUES
    summary: str = ""
    
    # Detailed findings
    key_findings: List[str] = field(default_factory=list)
    recommendations: Dict[str, List[str]] = field(default_factory=lambda: {
        'high_priority': [],
        'medium_priority': [],
        'low_priority': []
    })
    
    # Formula validation
    verified_formulas: List[str] = field(default_factory=list)
    questionable_formulas: List[str] = field(default_factory=list)
    incorrect_formulas: List[str] = field(default_factory=list)
    
    # Code compliance
    code_compliance: Dict[str, str] = field(default_factory=dict)
    
    # Optimization suggestions
    optimization_suggestions: List[str] = field(default_factory=list)
    
    # Metadata
    validation_timestamp: datetime = field(default_factory=datetime.now)
    claude_model: str = "claude-sonnet-4-20250514"
    
    def add_finding(self, finding: str):
        """Add a key finding"""
        self.key_findings.append(finding)
    
    def add_recommendation(self, priority: str, recommendation: str):
        """Add a recommendation with priority"""
        if priority in self.recommendations:
            self.recommendations[priority].append(recommendation)

# Utility functions for data structures
def create_default_bridge_configuration() -> BridgeConfiguration:
    """Create default bridge configuration"""
    return BridgeConfiguration(
        bridge_name="New Bridge Project",
        location="To be specified",
        span_length=10.0,
        bridge_width=7.5,
        num_spans=1,
        design_code=DesignCode.IRC_112.value,
        concrete_grade=ConcreteGrade.M25.value,
        steel_grade=SteelGrade.Fe415.value
    )

def create_default_material_properties() -> MaterialProperties:
    """Create default material properties"""
    return MaterialProperties(
        concrete_grade=ConcreteGrade.M25,
        steel_grade=SteelGrade.Fe415,
        concrete_strength=25.0,
        steel_yield_strength=415.0
    )

def create_default_soil_properties() -> SoilProperties:
    """Create default soil properties"""
    return SoilProperties(
        soil_type="Medium Dense Sand",
        unit_weight=18.0,
        angle_of_friction=30.0,
        bearing_capacity=450.0
    )

def validate_configuration(config: BridgeConfiguration) -> List[str]:
    """Validate bridge configuration and return list of errors"""
    errors = []
    
    if config.span_length <= 0:
        errors.append("Span length must be positive")
    
    if config.bridge_width <= 0:
        errors.append("Bridge width must be positive")
    
    if config.num_spans <= 0:
        errors.append("Number of spans must be positive")
    
    if not 0 <= config.skew_angle <= 60:
        errors.append("Skew angle must be between 0 and 60 degrees")
    
    if config.carriageway_width > config.bridge_width:
        errors.append("Carriageway width cannot exceed bridge width")
    
    return errors

def merge_analysis_results(results_list: List[AnalysisResults]) -> AnalysisResults:
    """Merge multiple analysis results into one"""
    if not results_list:
        return AnalysisResults()
    
    merged = AnalysisResults(
        analysis_type="Combined Analysis",
        status="PASS",
        max_stress=max(r.max_stress for r in results_list),
        max_deflection=max(r.max_deflection for r in results_list),
        max_moment=max(r.max_moment for r in results_list),
        max_shear=max(r.max_shear for r in results_list)
    )
    
    # Combine recommendations
    all_recommendations = []
    for result in results_list:
        all_recommendations.extend(result.recommendations)
    merged.recommendations = list(set(all_recommendations))
    
    # Overall status - fail if any individual analysis fails
    if any(r.status == "FAIL" for r in results_list):
        merged.status = "FAIL"
    elif any(r.status == "WARNING" for r in results_list):
        merged.status = "WARNING"
    
    return merged

# Constants for engineering calculations
ENGINEERING_CONSTANTS = {
    'pi': np.pi,
    'e': np.e,
    'gravity': 9.81,  # m/s²
    'steel_density': 7850,  # kg/m³
    'concrete_density': 2500,  # kg/m³
    'water_density': 1000,  # kg/m³
    'atmospheric_pressure': 101.325,  # kPa
    'steel_modulus': 200000,  # MPa
    'concrete_modulus_factor': 5000,  # Factor for concrete modulus calculation
}

# Standard load factors as per Indian codes
LOAD_FACTORS = {
    'IRC_6': {
        'dead_load': 1.35,
        'live_load': 1.75,
        'wind_load': 1.50,
        'seismic': 1.50,
        'temperature': 1.20
    },
    'IRC_112': {
        'dead_load': 1.35,
        'live_load': 1.50,
        'wind_load': 1.50,
        'seismic': 1.50,
        'temperature': 1.20
    }
}

# Material property tables
CONCRETE_PROPERTIES = {
    'M20': {'fck': 20, 'density': 25, 'modulus': 22000},
    'M25': {'fck': 25, 'density': 25, 'modulus': 25000},
    'M30': {'fck': 30, 'density': 25, 'modulus': 27000},
    'M35': {'fck': 35, 'density': 25, 'modulus': 29000},
    'M40': {'fck': 40, 'density': 25, 'modulus': 31000},
    'M45': {'fck': 45, 'density': 25, 'modulus': 33000},
    'M50': {'fck': 50, 'density': 25, 'modulus': 35000}
}

STEEL_PROPERTIES = {
    'Fe415': {'fy': 415, 'fu': 500, 'density': 78.5, 'modulus': 200000},
    'Fe500': {'fy': 500, 'fu': 550, 'density': 78.5, 'modulus': 200000},
    'Fe550': {'fy': 550, 'fu': 600, 'density': 78.5, 'modulus': 200000},
    'Fe600': {'fy': 600, 'fu': 675, 'density': 78.5, 'modulus': 200000}
}
