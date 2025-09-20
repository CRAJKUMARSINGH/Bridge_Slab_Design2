"""
Abutment Designer Module
Based on abutment design Excel sheets from PROJECT FILES
Implements Type-1 Battered and Type-2 Cantilever abutment designs
"""

import numpy as np
import pandas as pd
import math
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class AbutmentType(Enum):
    TYPE_1_BATTERED = "Type-1 Battered Faces"
    TYPE_2_CANTILEVER = "Type-2 Cantilever"
    TYPE_3_COUNTERFORT = "Type-3 Counterfort"

@dataclass
class AbutmentGeometry:
    """Abutment geometric parameters"""
    height: float                # Total height in m
    stem_thickness_top: float    # Stem thickness at top in m
    stem_thickness_base: float   # Stem thickness at base in m
    base_length: float          # Base length in m
    base_width: float           # Base width in m
    heel_length: float          # Heel length in m
    toe_length: float           # Toe length in m
    wing_wall_length: float     # Wing wall length in m
    wing_wall_thickness: float  # Wing wall thickness in m

class AbutmentDesigner:
    """Abutment design based on PROJECT FILES Excel formulas"""
    
    def __init__(self, project_data):
        self.project_data = project_data
        self.design_constants = self._initialize_design_constants()
        self.material_properties = self._initialize_material_properties()
    
    def _initialize_design_constants(self) -> Dict[str, float]:
        """Initialize design constants from PROJECT FILES"""
        return {
            'gamma_concrete': 25.0,  # kN/m³
            'gamma_soil': 18.0,      # kN/m³
            'gamma_water': 10.0,     # kN/m³
            'angle_friction': 30.0,   # degrees
            'bearing_capacity': 450.0, # kN/m²
            'coefficient_friction': 0.5,
            'safety_factor_overturning': 2.0,
            'safety_factor_sliding': 1.5,
            'concrete_cover': 75,     # mm
            'max_spacing': 300,       # mm
            'min_spacing': 100        # mm
        }
    
    def _initialize_material_properties(self) -> Dict[str, float]:
        """Initialize material properties"""
        return {
            'fck': 25,      # N/mm² - M25 concrete
            'fy': 415,      # N/mm² - Fe415 steel
            'es': 200000,   # N/mm² - Steel modulus
            'ec': 25000,    # N/mm² - Concrete modulus
            'gamma_c': 1.5, # Partial safety factor for concrete
            'gamma_s': 1.15 # Partial safety factor for steel
        }
    
    def design(self, design_params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform complete abutment design"""
        
        # Extract design parameters
        abutment_type = design_params.get('type', 'Type-1 Battered Faces')
        height = design_params.get('height', 6.5)
        sbc = design_params.get('sbc', 450.0)
        
        # Create abutment geometry
        geometry = self._design_geometry(abutment_type, height, design_params)
        
        # Calculate loads
        loads = self._calculate_abutment_loads(geometry, design_params)
        
        # Stability analysis
        stability = self._analyze_abutment_stability(geometry, loads, design_params)
        
        # Foundation design
        foundation = self._design_foundation(geometry, loads, stability, design_params)
        
        # Reinforcement design
        reinforcement = self._design_reinforcement(geometry, loads, design_params)
        
        # Overall design status
        design_status = self._determine_design_status(stability, foundation)
        
        return {
            'abutment_type': abutment_type,
            'geometry': geometry.__dict__,
            'loads': loads,
            'stability': stability,
            'foundation': foundation,
            'reinforcement': reinforcement,
            'design_status': design_status,
            'final_height': geometry.height,
            'final_base_length': geometry.base_length,
            'final_base_width': geometry.base_width,
            'final_stem_top': geometry.stem_thickness_top,
            'final_stem_base': geometry.stem_thickness_base,
            'concrete_volume': self._calculate_concrete_volume(geometry),
            'steel_weight': self._calculate_steel_weight(reinforcement),
            'overturning_factor': stability.get('overturning_factor', 0),
            'sliding_factor': stability.get('sliding_factor', 0),
            'max_pressure': stability.get('max_pressure', 0),
            'stability_details': stability
        }
    
    def _design_geometry(self, abutment_type: str, height: float, params: Dict[str, Any]) -> AbutmentGeometry:
        """Design abutment geometry based on type and parameters"""
        
        if abutment_type == "Type-1 Battered Faces":
            return self._design_battered_geometry(height, params)
        elif abutment_type == "Type-2 Cantilever":
            return self._design_cantilever_geometry(height, params)
        else:
            return self._design_counterfort_geometry(height, params)
    
    def _design_battered_geometry(self, height: float, params: Dict[str, Any]) -> AbutmentGeometry:
        """Design Type-1 battered faces abutment geometry"""
        
        # Proportions based on PROJECT FILES examples
        stem_top = max(0.3, height / 15)  # Minimum 300mm, approximately H/15
        stem_base = max(0.6, height / 8)  # Minimum 600mm, approximately H/8
        
        # Base dimensions
        base_length = max(4.0, 0.7 * height)  # 70% of height, minimum 4m
        base_width = max(2.0, 0.4 * height)   # 40% of height, minimum 2m
        
        # Heel and toe proportions
        heel_length = 0.6 * base_length  # 60% for heel
        toe_length = 0.4 * base_length   # 40% for toe
        
        # Wing walls (if required)
        wing_wall_length = height * 0.8  # 80% of abutment height
        wing_wall_thickness = max(0.3, stem_top)  # Same as stem top, minimum 300mm
        
        return AbutmentGeometry(
            height=height,
            stem_thickness_top=stem_top,
            stem_thickness_base=stem_base,
            base_length=base_length,
            base_width=base_width,
            heel_length=heel_length,
            toe_length=toe_length,
            wing_wall_length=wing_wall_length,
            wing_wall_thickness=wing_wall_thickness
        )
    
    def _design_cantilever_geometry(self, height: float, params: Dict[str, Any]) -> AbutmentGeometry:
        """Design Type-2 cantilever abutment geometry"""
        
        # Cantilever proportions (more slender)
        stem_top = max(0.25, height / 20)  # Thinner top for cantilever
        stem_base = max(0.5, height / 10)  # Base thickness
        
        # Base dimensions (larger for cantilever action)
        base_length = max(4.5, 0.8 * height)  # 80% of height
        base_width = max(2.2, 0.45 * height)  # 45% of height
        
        # Heel and toe proportions (favor heel for cantilever)
        heel_length = 0.7 * base_length  # 70% for heel (larger for moment resistance)
        toe_length = 0.3 * base_length   # 30% for toe
        
        # Wing walls
        wing_wall_length = height * 0.75  # Slightly shorter for cantilever
        wing_wall_thickness = stem_top     # Same as stem top
        
        return AbutmentGeometry(
            height=height,
            stem_thickness_top=stem_top,
            stem_thickness_base=stem_base,
            base_length=base_length,
            base_width=base_width,
            heel_length=heel_length,
            toe_length=toe_length,
            wing_wall_length=wing_wall_length,
            wing_wall_thickness=wing_wall_thickness
        )
    
    def _design_counterfort_geometry(self, height: float, params: Dict[str, Any]) -> AbutmentGeometry:
        """Design Type-3 counterfort abutment geometry"""
        
        # Counterfort allows thinner stem
        stem_top = max(0.2, height / 25)   # Very thin top
        stem_base = max(0.4, height / 12)  # Moderate base
        
        # Base dimensions
        base_length = max(5.0, 0.85 * height)  # Large base for counterfort
        base_width = max(2.5, 0.5 * height)    # Wide base
        
        # Heel and toe proportions
        heel_length = 0.75 * base_length  # Large heel for counterfort
        toe_length = 0.25 * base_length   # Small toe
        
        # Wing walls
        wing_wall_length = height * 0.9   # Longer for counterfort type
        wing_wall_thickness = stem_base * 0.8  # Proportional to stem base
        
        return AbutmentGeometry(
            height=height,
            stem_thickness_top=stem_top,
            stem_thickness_base=stem_base,
            base_length=base_length,
            base_width=base_width,
            heel_length=heel_length,
            toe_length=toe_length,
            wing_wall_length=wing_wall_length,
            wing_wall_thickness=wing_wall_thickness
        )
    
    def _calculate_abutment_loads(self, geometry: AbutmentGeometry, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate all loads acting on abutment"""
        
        # Dead loads
        dead_loads = self._calculate_dead_loads(geometry)
        
        # Earth pressure loads
        earth_pressure = self._calculate_earth_pressure(geometry, params)
        
        # Live load surcharge
        surcharge = self._calculate_surcharge_loads(geometry, params)
        
        # Seismic loads (if applicable)
        seismic = self._calculate_seismic_loads(geometry, dead_loads, earth_pressure, params)
        
        # Water pressure (if applicable)
        water_pressure = self._calculate_water_pressure(geometry, params)
        
        # Bridge loads (reaction from superstructure)
        bridge_loads = self._calculate_bridge_reaction_loads(params)
        
        return {
            'dead_loads': dead_loads,
            'earth_pressure': earth_pressure,
            'surcharge': surcharge,
            'seismic': seismic,
            'water_pressure': water_pressure,
            'bridge_loads': bridge_loads,
            'total_vertical': dead_loads['total'] + bridge_loads['vertical'],
            'total_horizontal': earth_pressure['total'] + surcharge['horizontal'] + seismic['horizontal']
        }
    
    def _calculate_dead_loads(self, geometry: AbutmentGeometry) -> Dict[str, float]:
        """Calculate dead loads of abutment structure"""
        
        gamma_c = self.design_constants['gamma_concrete']
        
        # Stem weight (trapezoidal section)
        stem_volume = 0.5 * (geometry.stem_thickness_top + geometry.stem_thickness_base) * geometry.height * geometry.base_width
        stem_weight = stem_volume * gamma_c
        
        # Base slab weight
        base_volume = geometry.base_length * geometry.base_width * geometry.stem_thickness_base
        base_weight = base_volume * gamma_c
        
        # Wing wall weight (simplified as rectangular)
        wing_volume = 2 * geometry.wing_wall_length * geometry.height * geometry.wing_wall_thickness
        wing_weight = wing_volume * gamma_c
        
        # Total dead load
        total_dead = stem_weight + base_weight + wing_weight
        
        return {
            'stem_weight': stem_weight,
            'base_weight': base_weight,
            'wing_weight': wing_weight,
            'total': total_dead,
            'stem_location_x': geometry.toe_length + geometry.stem_thickness_base / 2,
            'base_location_x': geometry.base_length / 2,
            'wing_location_x': geometry.toe_length + geometry.stem_thickness_base / 2
        }
    
    def _calculate_earth_pressure(self, geometry: AbutmentGeometry, params: Dict[str, Any]) -> Dict[str, float]:
        """Calculate active earth pressure"""
        
        gamma_soil = params.get('unit_weight', self.design_constants['gamma_soil'])
        phi = params.get('angle_friction', self.design_constants['angle_friction'])
        
        # Active earth pressure coefficient
        phi_rad = math.radians(phi)
        ka = math.tan(math.radians(45 - phi/2))**2  # Rankine's formula
        
        # Active pressure at base
        pressure_at_base = ka * gamma_soil * geometry.height
        
        # Total active force
        total_force = 0.5 * pressure_at_base * geometry.height
        
        # Height of application (from base)
        force_height = geometry.height / 3
        
        return {
            'ka': ka,
            'pressure_at_base': pressure_at_base,
            'total': total_force,
            'height_of_application': force_height,
            'moment_arm': force_height  # About base
        }
    
    def _calculate_surcharge_loads(self, geometry: AbutmentGeometry, params: Dict[str, Any]) -> Dict[str, float]:
        """Calculate surcharge loads"""
        
        surcharge_load = params.get('surcharge_load', 10.0)  # kN/m²
        gamma_soil = params.get('unit_weight', self.design_constants['gamma_soil'])
        phi = params.get('angle_friction', self.design_constants['angle_friction'])
        
        # Active earth pressure coefficient
        phi_rad = math.radians(phi)
        ka = math.tan(math.radians(45 - phi/2))**2
        
        # Horizontal force due to surcharge
        horizontal_force = ka * surcharge_load * geometry.height
        
        # Vertical load on heel (if any)
        vertical_load = surcharge_load * geometry.heel_length
        
        return {
            'surcharge_intensity': surcharge_load,
            'horizontal': horizontal_force,
            'vertical': vertical_load,
            'height_of_application': geometry.height / 2,
            'vertical_location_x': geometry.toe_length + geometry.stem_thickness_base + geometry.heel_length / 2
        }
    
    def _calculate_seismic_loads(self, geometry: AbutmentGeometry, dead_loads: Dict[str, float],
                                earth_pressure: Dict[str, float], params: Dict[str, Any]) -> Dict[str, float]:
        """Calculate seismic loads"""
        
        seismic_coeff = params.get('seismic_coefficient', 0.1)  # Horizontal seismic coefficient
        
        # Seismic force on structure
        structure_seismic = seismic_coeff * dead_loads['total']
        
        # Seismic force on soil (additional to static earth pressure)
        soil_seismic = seismic_coeff * earth_pressure['total']
        
        # Total horizontal seismic force
        total_horizontal = structure_seismic + soil_seismic
        
        return {
            'coefficient': seismic_coeff,
            'structure_seismic': structure_seismic,
            'soil_seismic': soil_seismic,
            'horizontal': total_horizontal,
            'vertical': 0,  # Vertical seismic usually neglected for abutments
            'height_of_application': geometry.height / 2
        }
    
    def _calculate_water_pressure(self, geometry: AbutmentGeometry, params: Dict[str, Any]) -> Dict[str, float]:
        """Calculate water pressure (if applicable)"""
        
        water_level = params.get('water_level', 0)  # Height of water above base
        gamma_water = self.design_constants['gamma_water']
        
        if water_level > 0:
            # Hydrostatic pressure
            pressure_at_base = gamma_water * water_level
            total_force = 0.5 * pressure_at_base * water_level
            force_height = water_level / 3
        else:
            pressure_at_base = 0
            total_force = 0
            force_height = 0
        
        return {
            'water_level': water_level,
            'pressure_at_base': pressure_at_base,
            'total': total_force,
            'height_of_application': force_height
        }
    
    def _calculate_bridge_reaction_loads(self, params: Dict[str, Any]) -> Dict[str, float]:
        """Calculate loads from bridge superstructure"""
        
        # Simplified bridge reaction calculation
        span_length = getattr(self.project_data, 'span_length', 10.0)
        bridge_width = getattr(self.project_data, 'bridge_width', 7.5)
        
        # Dead load reaction (approximate)
        slab_thickness = 0.5  # Assumed slab thickness
        dead_load_reaction = 25 * slab_thickness * bridge_width * span_length / 2  # Per abutment
        
        # Live load reaction (approximate)
        live_load_intensity = 5.0  # kN/m² (Class A loading)
        live_load_reaction = live_load_intensity * bridge_width * span_length / 2  # Per abutment
        
        # Total vertical reaction
        total_vertical = dead_load_reaction + live_load_reaction
        
        # Horizontal load (braking, temperature, etc.)
        horizontal_load = 0.2 * live_load_reaction  # 20% of live load
        
        return {
            'dead_load_reaction': dead_load_reaction,
            'live_load_reaction': live_load_reaction,
            'vertical': total_vertical,
            'horizontal': horizontal_load,
            'vertical_location_x': 0,  # Assumed at bearing location
            'horizontal_height': getattr(self.project_data, 'span_length', 10.0) / 20  # Deck level
        }
    
    def _analyze_abutment_stability(self, geometry: AbutmentGeometry, loads: Dict[str, Any],
                                   params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze abutment stability"""
        
        # Overturning analysis
        overturning = self._check_overturning(geometry, loads)
        
        # Sliding analysis
        sliding = self._check_sliding(geometry, loads, params)
        
        # Bearing pressure analysis
        bearing = self._check_bearing_pressure(geometry, loads, params)
        
        return {
            'overturning': overturning,
            'sliding': sliding,
            'bearing': bearing,
            'overturning_factor': overturning['safety_factor'],
            'sliding_factor': sliding['safety_factor'],
            'max_pressure': bearing['max_pressure'],
            'overall_status': 'SAFE' if all([overturning['is_safe'], sliding['is_safe'], bearing['is_safe']]) else 'UNSAFE'
        }
    
    def _check_overturning(self, geometry: AbutmentGeometry, loads: Dict[str, Any]) -> Dict[str, Any]:
        """Check overturning stability"""
        
        # Overturning moments about toe
        earth_moment = loads['earth_pressure']['total'] * loads['earth_pressure']['height_of_application']
        surcharge_moment = loads['surcharge']['horizontal'] * loads['surcharge']['height_of_application']
        seismic_moment = loads['seismic']['horizontal'] * loads['seismic']['height_of_application']
        bridge_h_moment = loads['bridge_loads']['horizontal'] * loads['bridge_loads']['horizontal_height']
        
        total_overturning = earth_moment + surcharge_moment + seismic_moment + bridge_h_moment
        
        # Resisting moments about toe
        dead_moment = loads['dead_loads']['total'] * loads['dead_loads']['base_location_x']
        bridge_v_moment = loads['bridge_loads']['vertical'] * loads['bridge_loads']['vertical_location_x']
        surcharge_v_moment = loads['surcharge']['vertical'] * loads['surcharge']['vertical_location_x']
        
        total_resisting = dead_moment + bridge_v_moment + surcharge_v_moment
        
        # Safety factor
        safety_factor = total_resisting / max(total_overturning, 1e-6)
        is_safe = safety_factor >= self.design_constants['safety_factor_overturning']
        
        return {
            'overturning_moment': total_overturning,
            'resisting_moment': total_resisting,
            'safety_factor': safety_factor,
            'required_factor': self.design_constants['safety_factor_overturning'],
            'is_safe': is_safe
        }
    
    def _check_sliding(self, geometry: AbutmentGeometry, loads: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Check sliding stability"""
        
        # Driving forces
        driving_force = loads['total_horizontal']
        
        # Resisting forces
        normal_force = loads['total_vertical']
        friction_coeff = params.get('friction_coefficient', self.design_constants['coefficient_friction'])
        friction_resistance = normal_force * friction_coeff
        
        # Cohesion resistance
        cohesion = params.get('cohesion', 15.0)
        base_area = geometry.base_length * geometry.base_width
        cohesion_resistance = cohesion * base_area
        
        # Passive resistance (if applicable)
        passive_resistance = 0  # Simplified - usually requires detailed analysis
        
        total_resistance = friction_resistance + cohesion_resistance + passive_resistance
        
        # Safety factor
        safety_factor = total_resistance / max(driving_force, 1e-6)
        is_safe = safety_factor >= self.design_constants['safety_factor_sliding']
        
        return {
            'driving_force': driving_force,
            'friction_resistance': friction_resistance,
            'cohesion_resistance': cohesion_resistance,
            'total_resistance': total_resistance,
            'safety_factor': safety_factor,
            'required_factor': self.design_constants['safety_factor_sliding'],
            'is_safe': is_safe
        }
    
    def _check_bearing_pressure(self, geometry: AbutmentGeometry, loads: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Check bearing pressure distribution"""
        
        # Total vertical load and moment
        V = loads['total_vertical']
        M = (loads['earth_pressure']['total'] * loads['earth_pressure']['height_of_application'] +
             loads['surcharge']['horizontal'] * loads['surcharge']['height_of_application'] +
             loads['seismic']['horizontal'] * loads['seismic']['height_of_application'])
        
        # Eccentricity
        e = M / V if V > 0 else 0
        
        # Base dimensions
        B = geometry.base_length
        
        # Check if resultant is within middle third
        middle_third = B / 6
        within_middle_third = e <= middle_third
        
        # Pressure calculation
        if within_middle_third:
            q_max = (V / B) * (1 + 6 * e / B)
            q_min = (V / B) * (1 - 6 * e / B)
        else:
            # Triangular distribution
            effective_length = 3 * (B/2 - e)
            q_max = 2 * V / effective_length
            q_min = 0
        
        # Check against bearing capacity
        bearing_capacity = params.get('sbc', self.design_constants['bearing_capacity'])
        is_safe = q_max <= bearing_capacity
        
        return {
            'total_load': V,
            'moment': M,
            'eccentricity': e,
            'max_pressure': q_max,
            'min_pressure': q_min,
            'bearing_capacity': bearing_capacity,
            'within_middle_third': within_middle_third,
            'is_safe': is_safe
        }
    
    def _design_foundation(self, geometry: AbutmentGeometry, loads: Dict[str, Any],
                          stability: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Design foundation system"""
        
        # Check if current base is adequate
        if stability['bearing']['is_safe'] and stability['overall_status'] == 'SAFE':
            foundation_type = 'SHALLOW_FOUNDATION'
            required_length = geometry.base_length
            required_width = geometry.base_width
        else:
            # Suggest foundation improvements
            foundation_type = 'IMPROVED_SHALLOW_FOUNDATION'
            
            # Increase base dimensions
            required_length = geometry.base_length * 1.2
            required_width = geometry.base_width * 1.2
            
            # Check if pile foundation is needed
            if stability['bearing']['max_pressure'] > params.get('sbc', 450) * 2:
                foundation_type = 'PILE_FOUNDATION'
        
        return {
            'foundation_type': foundation_type,
            'required_length': required_length,
            'required_width': required_width,
            'depth_of_foundation': max(2.0, geometry.height * 0.2),  # Minimum 2m or 20% of height
            'recommendation': self._get_foundation_recommendation(foundation_type, stability)
        }
    
    def _design_reinforcement(self, geometry: AbutmentGeometry, loads: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Design reinforcement for abutment"""
        
        # Material properties
        fck = self.material_properties['fck']
        fy = self.material_properties['fy']
        
        # Stem reinforcement design
        stem_reinforcement = self._design_stem_reinforcement(geometry, loads)
        
        # Base reinforcement design
        base_reinforcement = self._design_base_reinforcement(geometry, loads)
        
        # Wing wall reinforcement
        wing_reinforcement = self._design_wing_wall_reinforcement(geometry, loads)
        
        return {
            'stem_reinforcement': stem_reinforcement,
            'base_reinforcement': base_reinforcement,
            'wing_reinforcement': wing_reinforcement,
            'stem_main_bars': stem_reinforcement.get('main_bars', 'Not calculated'),
            'stem_dist_bars': stem_reinforcement.get('distribution_bars', 'Not calculated'),
            'stem_shear_bars': stem_reinforcement.get('shear_bars', 'Not calculated'),
            'base_long_bars': base_reinforcement.get('longitudinal_bars', 'Not calculated'),
            'base_trans_bars': base_reinforcement.get('transverse_bars', 'Not calculated')
        }
    
    def _design_stem_reinforcement(self, geometry: AbutmentGeometry, loads: Dict[str, Any]) -> Dict[str, Any]:
        """Design stem reinforcement"""
        
        # Maximum moment at base of stem
        earth_pressure = loads['earth_pressure']['total']
        moment_arm = loads['earth_pressure']['height_of_application']
        max_moment = earth_pressure * moment_arm  # kN-m per meter width
        
        # Effective depth
        d = geometry.stem_thickness_base * 1000 - self.design_constants['concrete_cover']  # mm
        
        # Required steel area (simplified)
        fy = self.material_properties['fy']
        required_area = (max_moment * 1e6) / (0.87 * fy * 0.9 * d)  # mm² per meter
        
        # Minimum steel requirement
        min_area = 0.12 * geometry.stem_thickness_base * 1000  # 0.12% of gross area
        
        # Provided steel area
        provided_area = max(required_area, min_area)
        
        return {
            'max_moment': max_moment,
            'required_area': required_area,
            'provided_area': provided_area,
            'main_bars': f"16mm @ 200mm c/c (Area: {provided_area:.0f} mm²/m)",
            'distribution_bars': "12mm @ 250mm c/c horizontal",
            'shear_bars': "8mm @ 200mm c/c stirrups"
        }
    
    def _design_base_reinforcement(self, geometry: AbutmentGeometry, loads: Dict[str, Any]) -> Dict[str, Any]:
        """Design base slab reinforcement"""
        
        # Soil pressure
        max_pressure = loads.get('bearing_analysis', {}).get('max_pressure', 200)  # kN/m²
        
        # Moment in base slab (heel cantilever)
        heel_moment = 0.5 * max_pressure * geometry.heel_length**2  # kN-m per meter
        
        # Required steel area
        d = geometry.stem_thickness_base * 1000 - self.design_constants['concrete_cover']  # mm
        fy = self.material_properties['fy']
        required_area = (heel_moment * 1e6) / (0.87 * fy * 0.9 * d)  # mm² per meter
        
        # Minimum steel
        min_area = 0.12 * geometry.stem_thickness_base * 1000  # 0.12%
        
        provided_area = max(required_area, min_area)
        
        return {
            'heel_moment': heel_moment,
            'required_area': required_area,
            'provided_area': provided_area,
            'longitudinal_bars': f"16mm @ 200mm c/c (Area: {provided_area:.0f} mm²/m)",
            'transverse_bars': "12mm @ 250mm c/c"
        }
    
    def _design_wing_wall_reinforcement(self, geometry: AbutmentGeometry, loads: Dict[str, Any]) -> Dict[str, Any]:
        """Design wing wall reinforcement"""
        
        # Earth pressure on wing wall
        wing_pressure = 0.5 * self.design_constants['gamma_soil'] * geometry.height**2 * 0.3  # Reduced for wing wall
        
        # Required steel (simplified)
        required_area = wing_pressure * 0.01  # Simplified calculation
        min_area = 0.12 * geometry.wing_wall_thickness * 1000  # 0.12%
        
        provided_area = max(required_area, min_area)
        
        return {
            'wing_pressure': wing_pressure,
            'required_area': required_area,
            'provided_area': provided_area,
            'vertical_bars': "12mm @ 200mm c/c",
            'horizontal_bars': "10mm @ 250mm c/c"
        }
    
    def _calculate_concrete_volume(self, geometry: AbutmentGeometry) -> float:
        """Calculate total concrete volume"""
        
        # Stem volume (trapezoidal)
        stem_volume = 0.5 * (geometry.stem_thickness_top + geometry.stem_thickness_base) * geometry.height * geometry.base_width
        
        # Base volume
        base_volume = geometry.base_length * geometry.base_width * geometry.stem_thickness_base
        
        # Wing wall volume
        wing_volume = 2 * geometry.wing_wall_length * geometry.height * geometry.wing_wall_thickness
        
        return stem_volume + base_volume + wing_volume
    
    def _calculate_steel_weight(self, reinforcement: Dict[str, Any]) -> float:
        """Calculate total steel weight"""
        
        # Simplified calculation based on typical reinforcement ratios
        concrete_volume = getattr(self, '_last_concrete_volume', 100)  # Default if not available
        steel_ratio = 0.015  # 1.5% typical for abutments
        steel_volume = concrete_volume * steel_ratio
        steel_weight = steel_volume * 7850  # kg (steel density)
        
        return steel_weight
    
    def _determine_design_status(self, stability: Dict[str, Any], foundation: Dict[str, Any]) -> str:
        """Determine overall design status"""
        
        if stability['overall_status'] == 'SAFE' and foundation['foundation_type'] == 'SHALLOW_FOUNDATION':
            return 'SAFE'
        elif stability['overall_status'] == 'SAFE':
            return 'SAFE_WITH_FOUNDATION_IMPROVEMENT'
        else:
            return 'NEEDS_REVISION'
    
    def _get_foundation_recommendation(self, foundation_type: str, stability: Dict[str, Any]) -> str:
        """Get foundation recommendation based on analysis"""
        
        if foundation_type == 'SHALLOW_FOUNDATION':
            return "Current foundation dimensions are adequate"
        elif foundation_type == 'IMPROVED_SHALLOW_FOUNDATION':
            return "Increase foundation dimensions or improve soil bearing capacity"
        else:
            return "Deep foundation (piles) required due to poor soil conditions"

