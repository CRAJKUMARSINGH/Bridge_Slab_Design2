"""
Bridge Designer Module
Core bridge design calculations based on PROJECT FILES
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import math
from enum import Enum

class BridgeType(Enum):
    SUBMERSIBLE = "Submersible Bridge"
    HIGH_LEVEL = "High Level Bridge"
    AQUEDUCT = "Aqueduct"
    CULVERT = "Culvert"

class LoadClass(Enum):
    CLASS_A = "Class A"
    CLASS_AA = "Class AA"
    CLASS_70R = "Class 70R"
    CLASS_A_70R = "Class A + 70R"

@dataclass
class BridgeConfiguration:
    """Bridge configuration based on PROJECT FILES structure"""
    bridge_name: str
    location: str
    project_type: str
    span_length: float
    bridge_width: float
    num_spans: int
    skew_angle: float
    design_code: str
    concrete_grade: str
    steel_grade: str
    design_life: int
    
    def __post_init__(self):
        """Validate configuration parameters"""
        if self.span_length <= 0:
            raise ValueError("Span length must be positive")
        if self.bridge_width <= 0:
            raise ValueError("Bridge width must be positive")
        if not 0 <= self.skew_angle <= 55:
            raise ValueError("Skew angle must be between 0 and 55 degrees")

class BridgeDesigner:
    """Main bridge designer class based on extracted Excel formulas"""
    
    def __init__(self, config: BridgeConfiguration):
        self.config = config
        self.material_properties = self._initialize_material_properties()
        self.load_factors = self._initialize_load_factors()
        self.design_constants = self._initialize_design_constants()
    
    def _initialize_material_properties(self) -> Dict[str, float]:
        """Initialize material properties based on grades"""
        
        # Concrete properties
        concrete_grades = {
            'M25': {'fck': 25, 'density': 25.0, 'modulus': 25000},
            'M30': {'fck': 30, 'density': 25.0, 'modulus': 27000},
            'M35': {'fck': 35, 'density': 25.0, 'modulus': 29000},
            'M40': {'fck': 40, 'density': 25.0, 'modulus': 31000}
        }
        
        # Steel properties
        steel_grades = {
            'Fe415': {'fy': 415, 'es': 200000, 'density': 78.5},
            'Fe500': {'fy': 500, 'es': 200000, 'density': 78.5},
            'Fe550': {'fy': 550, 'es': 200000, 'density': 78.5}
        }
        
        properties = {}
        
        # Get concrete properties
        if self.config.concrete_grade in concrete_grades:
            concrete = concrete_grades[self.config.concrete_grade]
            properties.update({
                'fck': concrete['fck'],  # N/mm²
                'concrete_density': concrete['density'],  # kN/m³
                'ec': concrete['modulus']  # N/mm²
            })
        
        # Get steel properties
        if self.config.steel_grade in steel_grades:
            steel = steel_grades[self.config.steel_grade]
            properties.update({
                'fy': steel['fy'],  # N/mm²
                'es': steel['es'],  # N/mm²
                'steel_density': steel['density']  # kN/m³
            })
        
        return properties
    
    def _initialize_load_factors(self) -> Dict[str, float]:
        """Initialize load factors based on design code"""
        
        if self.config.design_code == "IRC-6":
            return {
                'dead_load': 1.35,
                'live_load': 1.75,
                'live_load_secondary': 1.20,
                'wind_load': 1.50,
                'seismic': 1.50,
                'temperature': 1.20
            }
        elif self.config.design_code == "IRC-112":
            return {
                'dead_load': 1.35,
                'live_load': 1.50,
                'live_load_secondary': 1.20,
                'wind_load': 1.50,
                'seismic': 1.50,
                'temperature': 1.20
            }
        else:
            # Default factors
            return {
                'dead_load': 1.35,
                'live_load': 1.75,
                'live_load_secondary': 1.20,
                'wind_load': 1.50,
                'seismic': 1.50,
                'temperature': 1.20
            }
    
    def _initialize_design_constants(self) -> Dict[str, float]:
        """Initialize design constants from PROJECT FILES"""
        
        return {
            'gamma_c': 1.5,  # Partial safety factor for concrete
            'gamma_s': 1.15,  # Partial safety factor for steel
            'alpha_cc': 0.67,  # Factor for concrete strength in flexure
            'beta_1': 0.80,  # Stress block factor
            'max_compression_strain': 0.0035,  # Maximum compression strain
            'max_tension_strain': 0.002,  # Maximum tension strain
            'cover_slab': 50,  # mm, clear cover for slab
            'cover_beam': 50,  # mm, clear cover for beam
            'cover_column': 75,  # mm, clear cover for column
        }
    
    def calculate_dead_loads(self) -> Dict[str, float]:
        """Calculate dead loads based on bridge configuration"""
        
        # Main structural dead load
        slab_thickness = self._estimate_slab_thickness()
        slab_volume_per_meter = slab_thickness * self.config.bridge_width * 1.0  # per meter length
        slab_dead_load = slab_volume_per_meter * self.material_properties.get('concrete_density', 25.0)
        
        # Wearing coat (typically 75mm thick)
        wearing_coat_thickness = 0.075  # m
        wearing_coat_density = 22.0  # kN/m³
        wearing_coat_load = wearing_coat_thickness * self.config.bridge_width * wearing_coat_density
        
        # Crash barriers and railings
        crash_barrier_load = 2.0 * 3.0  # kN/m (2 barriers × 3 kN/m each)
        
        # Utilities and services
        utilities_load = 1.0  # kN/m
        
        total_dead_load = slab_dead_load + wearing_coat_load + crash_barrier_load + utilities_load
        
        return {
            'slab_self_weight': slab_dead_load,
            'wearing_coat': wearing_coat_load,
            'crash_barriers': crash_barrier_load,
            'utilities': utilities_load,
            'total_dead_load': total_dead_load,
            'dead_load_per_sqm': total_dead_load / self.config.bridge_width
        }
    
    def calculate_live_loads(self, load_class: LoadClass = LoadClass.CLASS_A) -> Dict[str, float]:
        """Calculate live loads based on IRC specifications"""
        
        if load_class == LoadClass.CLASS_A:
            # IRC Class A loading
            udl = 5.0  # kN/m² over carriageway
            concentrated_load = 27.0  # kN on 0.3m × 0.3m area
            
        elif load_class == LoadClass.CLASS_AA:
            # IRC Class AA loading
            udl = 8.0  # kN/m²
            concentrated_load = 40.0  # kN
            
        elif load_class == LoadClass.CLASS_70R:
            # IRC Class 70R tracked vehicle
            track_load = 700.0  # kN total
            track_length = 3.6  # m
            track_width = 0.84  # m
            contact_pressure = track_load / (track_length * track_width)
            
            return {
                'track_load_total': track_load,
                'track_pressure': contact_pressure,
                'equivalent_udl': contact_pressure * 0.5,  # Equivalent UDL
                'impact_factor': self._calculate_impact_factor()
            }
        
        else:  # CLASS_A_70R combination
            # Consider both Class A and 70R
            class_a_udl = 5.0
            track_equivalent = 350.0 / (self.config.span_length * self.config.bridge_width)
            
            udl = max(class_a_udl, track_equivalent)
            concentrated_load = 40.0  # Higher of Class A and AA
        
        # Calculate impact factor
        impact_factor = self._calculate_impact_factor()
        
        # Effective live load per unit area
        carriageway_width = min(self.config.bridge_width - 2.0, 7.5)  # Effective carriageway
        total_live_load = udl * carriageway_width
        
        return {
            'udl': udl,
            'concentrated_load': concentrated_load,
            'carriageway_width': carriageway_width,
            'total_live_load': total_live_load,
            'impact_factor': impact_factor,
            'live_load_with_impact': total_live_load * (1 + impact_factor),
            'load_class': load_class.value
        }
    
    def _calculate_impact_factor(self) -> float:
        """Calculate impact factor based on span length (IRC-6)"""
        
        if self.config.span_length <= 9.0:
            return (9 - self.config.span_length) / 36
        elif self.config.span_length <= 12.0:
            return 0.0
        elif self.config.span_length <= 40.0:
            return (self.config.span_length - 12) / 125
        else:
            return 0.224
    
    def _estimate_slab_thickness(self) -> float:
        """Estimate slab thickness based on span and design requirements"""
        
        # Basic thickness estimation from span/depth ratio
        if self.config.project_type == "Submersible Bridge":
            # More conservative for submersible bridges
            min_thickness = self.config.span_length / 15  # L/15 to L/20
        else:
            min_thickness = self.config.span_length / 20  # L/20 to L/25
        
        # Minimum practical thickness
        min_practical = 0.20  # 200mm minimum
        
        # Maximum typical thickness
        max_practical = 1.20  # 1200mm maximum
        
        estimated_thickness = max(min_thickness, min_practical)
        estimated_thickness = min(estimated_thickness, max_practical)
        
        # Round to practical increments (50mm)
        return round(estimated_thickness * 20) / 20
    
    def design_main_reinforcement(self, moment: float, effective_depth: float) -> Dict[str, Any]:
        """Design main flexural reinforcement"""
        
        # Material properties
        fck = self.material_properties.get('fck', 25)
        fy = self.material_properties.get('fy', 415)
        gamma_c = self.design_constants['gamma_c']
        gamma_s = self.design_constants['gamma_s']
        
        # Design strengths
        fcd = fck / gamma_c
        fyd = fy / gamma_s
        
        # Effective depth
        d = effective_depth * 1000  # Convert to mm
        
        # Required area of steel
        # Using simplified rectangular stress block
        alpha = 0.36 * fcd  # Compressive stress
        
        # Balanced section analysis
        xu_max = 0.48 * d  # Maximum neutral axis depth
        
        # Required steel area calculation
        # M = 0.87 * fy * As * (d - 0.42 * xu)
        # Assuming xu = 0.48 * d for maximum moment capacity
        
        xu_assumed = 0.25 * d  # Conservative assumption
        
        # Required steel area
        As_required = (moment * 1e6) / (0.87 * fy * (d - 0.42 * xu_assumed))  # mm²
        
        # Minimum steel requirement
        As_min = 0.12 * self.config.bridge_width * 1000 * (self._estimate_slab_thickness() * 1000) / 100  # 0.12%
        
        # Maximum steel requirement  
        As_max = 4.0 * self.config.bridge_width * 1000 * (self._estimate_slab_thickness() * 1000) / 100  # 4.0%
        
        As_provided = max(As_required, As_min)
        As_provided = min(As_provided, As_max)
        
        # Bar selection
        bar_sizes = [12, 16, 20, 25, 32]  # Available bar sizes in mm
        bar_areas = {12: 113, 16: 201, 20: 314, 25: 491, 32: 804}  # mm²
        
        # Select optimal bar size and spacing
        selected_bars = []
        for bar_size in bar_sizes:
            area_per_bar = bar_areas[bar_size]
            num_bars = As_provided / area_per_bar
            spacing = (self.config.bridge_width * 1000) / num_bars
            
            if 100 <= spacing <= 300:  # Practical spacing range
                selected_bars.append({
                    'bar_size': bar_size,
                    'area_per_bar': area_per_bar,
                    'number_of_bars': int(num_bars) + 1,
                    'spacing': spacing,
                    'total_area': (int(num_bars) + 1) * area_per_bar
                })
        
        # Select the most economical option
        if selected_bars:
            optimal_bars = min(selected_bars, key=lambda x: x['total_area'])
        else:
            # Fallback option
            optimal_bars = {
                'bar_size': 16,
                'area_per_bar': 201,
                'number_of_bars': int(As_provided / 201) + 1,
                'spacing': 200,
                'total_area': (int(As_provided / 201) + 1) * 201
            }
        
        return {
            'required_area': As_required,
            'minimum_area': As_min,
            'provided_area': optimal_bars['total_area'],
            'bar_details': optimal_bars,
            'design_moment': moment,
            'effective_depth': effective_depth,
            'steel_ratio': optimal_bars['total_area'] / (self.config.bridge_width * 1000 * d) * 100,
            'design_status': 'SAFE' if optimal_bars['total_area'] >= As_required else 'UNSAFE'
        }
    
    def design_shear_reinforcement(self, shear_force: float, effective_depth: float) -> Dict[str, Any]:
        """Design shear reinforcement"""
        
        # Material properties
        fck = self.material_properties.get('fck', 25)
        fy = self.material_properties.get('fy', 415)
        
        # Design shear strength of concrete
        tau_c = 0.62 * math.sqrt(fck)  # N/mm² (simplified)
        
        # Shear stress
        b = self.config.bridge_width * 1000  # mm
        d = effective_depth * 1000  # mm
        
        tau_v = (shear_force * 1000) / (b * d)  # N/mm²
        
        # Check if shear reinforcement is required
        if tau_v <= tau_c:
            return {
                'shear_reinforcement_required': False,
                'design_shear_stress': tau_v,
                'permissible_shear_stress': tau_c,
                'design_status': 'SAFE_WITHOUT_SHEAR_REINFORCEMENT'
            }
        
        # Calculate required shear reinforcement
        tau_us = tau_v - tau_c  # Additional shear stress to be resisted
        
        # Shear reinforcement area per unit length
        # Asv/sv = tau_us * b / (0.87 * fy)
        
        asv_sv = (tau_us * b) / (0.87 * fy)  # mm²/mm
        
        # Select stirrup configuration
        stirrup_diameter = 8  # mm
        area_per_stirrup = 2 * math.pi * (stirrup_diameter/2)**2  # 2-legged stirrups
        
        required_spacing = area_per_stirrup / asv_sv  # mm
        
        # Practical spacing constraints
        max_spacing = min(0.75 * d, 300)  # mm
        min_spacing = 75  # mm
        
        provided_spacing = max(min(required_spacing, max_spacing), min_spacing)
        provided_spacing = round(provided_spacing / 25) * 25  # Round to 25mm increments
        
        # Minimum shear reinforcement check
        min_asv_sv = 0.4 / fy  # mm²/mm
        provided_asv_sv = area_per_stirrup / provided_spacing
        
        if provided_asv_sv < min_asv_sv:
            provided_spacing = area_per_stirrup / min_asv_sv
            provided_spacing = round(provided_spacing / 25) * 25
        
        return {
            'shear_reinforcement_required': True,
            'design_shear_stress': tau_v,
            'permissible_shear_stress': tau_c,
            'additional_shear_stress': tau_us,
            'stirrup_diameter': stirrup_diameter,
            'stirrup_spacing': provided_spacing,
            'provided_shear_area': area_per_stirrup / provided_spacing,
            'required_shear_area': asv_sv,
            'design_status': 'SAFE' if provided_asv_sv >= asv_sv else 'REVIEW_REQUIRED'
        }
    
    def calculate_deflection(self, moment: float, steel_area: float, effective_depth: float) -> Dict[str, float]:
        """Calculate deflection and check against limits"""
        
        # Material properties
        ec = self.material_properties.get('ec', 25000)  # N/mm²
        es = self.material_properties.get('es', 200000)  # N/mm²
        
        # Section properties
        b = self.config.bridge_width * 1000  # mm
        d = effective_depth * 1000  # mm
        
        # Modular ratio
        m = es / ec
        
        # Steel percentage
        pt = (steel_area / (b * d)) * 100
        
        # Neutral axis depth
        k = (-m * pt + math.sqrt((m * pt)**2 + 2 * m * pt)) / (1 + m * pt)
        
        # Moment of inertia of cracked section
        Icr = (b * (k * d)**3 / 3) + (m * steel_area * (d * (1 - k))**2)
        
        # Effective moment of inertia (simplified)
        Ie = Icr  # Using cracked section for simplicity
        
        # Deflection calculation (simply supported beam)
        # δ = 5 * w * L^4 / (384 * E * I)
        
        L = self.config.span_length * 1000  # mm
        
        # Convert moment to equivalent UDL
        w_equivalent = (8 * moment * 1e6) / (L**2)  # N/mm
        
        deflection = (5 * w_equivalent * L**4) / (384 * ec * Ie)  # mm
        
        # Deflection limits
        deflection_limit = L / 250  # mm (span/250 for bridges)
        service_limit = L / 350  # mm (span/350 for serviceability)
        
        return {
            'calculated_deflection': deflection,
            'deflection_limit': deflection_limit,
            'service_limit': service_limit,
            'deflection_ratio': deflection / deflection_limit,
            'deflection_check': 'PASS' if deflection <= deflection_limit else 'FAIL',
            'serviceability_check': 'PASS' if deflection <= service_limit else 'FAIL'
        }
    
    def perform_complete_design(self) -> Dict[str, Any]:
        """Perform complete bridge design analysis"""
        
        # Calculate loads
        dead_loads = self.calculate_dead_loads()
        live_loads = self.calculate_live_loads()
        
        # Total design loads
        total_dead = dead_loads['total_dead_load']
        total_live = live_loads['live_load_with_impact']
        
        # Factored loads
        factored_dead = total_dead * self.load_factors['dead_load']
        factored_live = total_live * self.load_factors['live_load']
        
        total_factored_load = factored_dead + factored_live
        
        # Calculate design moments and shears (simply supported)
        design_moment = (total_factored_load * self.config.span_length**2) / 8  # kN-m
        design_shear = (total_factored_load * self.config.span_length) / 2  # kN
        
        # Estimate section properties
        slab_thickness = self._estimate_slab_thickness()
        effective_depth = slab_thickness - 0.05  # Assuming 50mm cover
        
        # Design reinforcement
        main_reinforcement = self.design_main_reinforcement(design_moment, effective_depth)
        shear_reinforcement = self.design_shear_reinforcement(design_shear, effective_depth)
        
        # Check deflection
        deflection_check = self.calculate_deflection(
            design_moment, 
            main_reinforcement['provided_area'], 
            effective_depth
        )
        
        # Overall design status
        design_checks = [
            main_reinforcement['design_status'] == 'SAFE',
            shear_reinforcement['design_status'] in ['SAFE', 'SAFE_WITHOUT_SHEAR_REINFORCEMENT'],
            deflection_check['deflection_check'] == 'PASS'
        ]
        
        overall_status = 'SAFE' if all(design_checks) else 'NEEDS_REVISION'
        
        return {
            'bridge_configuration': self.config.__dict__,
            'material_properties': self.material_properties,
            'load_analysis': {
                'dead_loads': dead_loads,
                'live_loads': live_loads,
                'factored_loads': {
                    'dead': factored_dead,
                    'live': factored_live,
                    'total': total_factored_load
                }
            },
            'design_forces': {
                'moment': design_moment,
                'shear': design_shear
            },
            'section_design': {
                'slab_thickness': slab_thickness,
                'effective_depth': effective_depth,
                'main_reinforcement': main_reinforcement,
                'shear_reinforcement': shear_reinforcement
            },
            'serviceability': {
                'deflection_check': deflection_check
            },
            'design_summary': {
                'overall_status': overall_status,
                'design_checks': design_checks,
                'recommendations': self._generate_recommendations(design_checks)
            }
        }
    
    def _generate_recommendations(self, design_checks: List[bool]) -> List[str]:
        """Generate design recommendations based on analysis results"""
        
        recommendations = []
        
        if not design_checks[0]:  # Main reinforcement issue
            recommendations.append("Increase slab thickness or use higher grade of steel for main reinforcement")
        
        if not design_checks[1]:  # Shear reinforcement issue
            recommendations.append("Provide adequate shear reinforcement or increase section depth")
        
        if not design_checks[2]:  # Deflection issue
            recommendations.append("Increase section depth or provide pre-stressed reinforcement to control deflection")
        
        if all(design_checks):
            recommendations.append("Design is satisfactory. Proceed with detailed drawings and specifications.")
        
        # Additional general recommendations
        recommendations.extend([
            "Ensure proper concrete cover as per exposure conditions",
            "Provide adequate drainage system to prevent water stagnation",
            "Consider seismic provisions if applicable to the location",
            "Include expansion joints for long bridges or temperature effects"
        ])
        
        return recommendations
