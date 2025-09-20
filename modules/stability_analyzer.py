"""
Stability Analyzer Module
Based on stability analysis Excel sheets from PROJECT FILES
Implements overturning, sliding, and bearing pressure checks
"""

import numpy as np
import pandas as pd
import math
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

@dataclass
class StabilityParameters:
    """Stability analysis parameters from Excel sheets"""
    structure_height: float  # Height of structure
    structure_width: float   # Width at base
    concrete_density: float  # Unit weight of concrete
    soil_density: float      # Unit weight of soil
    water_density: float     # Unit weight of water
    angle_of_friction: float # Soil friction angle in degrees
    cohesion: float         # Soil cohesion
    surcharge_load: float   # Surcharge load on backfill
    seismic_coefficient: float # Seismic coefficient
    safety_factor_sliding: float # Required safety factor for sliding
    safety_factor_overturning: float # Required safety factor for overturning
    bearing_capacity: float # Safe bearing capacity of soil

class StabilityAnalyzer:
    """Stability analysis based on PROJECT FILES Excel formulas"""
    
    def __init__(self, project_data):
        self.project_data = project_data
        self.calculation_steps = {}
        
    def analyze_from_excel_data(self, excel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze stability using data extracted from Excel files"""
        
        # Extract parameters from Excel data
        extracted_params = self._extract_stability_params(excel_data)
        
        # Perform stability analysis
        results = self.analyze_stability(extracted_params)
        
        # Add Excel-specific information
        results['excel_source'] = {
            'filename': excel_data.get('filename', 'unknown'),
            'sheets_processed': list(excel_data.get('sheets', {}).keys()),
            'formulas_used': self._identify_stability_formulas(excel_data)
        }
        
        results['calculation_steps'] = self.calculation_steps
        
        return results
    
    def analyze_stability(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform complete stability analysis"""
        
        # Convert to StabilityParameters
        stability_params = StabilityParameters(
            structure_height=params.get('structure_height', 6.5),
            structure_width=params.get('structure_width', 7.0),
            concrete_density=params.get('concrete_density', 24.0),
            soil_density=params.get('soil_density', 18.0),
            water_density=params.get('water_density', 10.0),
            angle_of_friction=params.get('angle_of_friction', 30.0),
            cohesion=params.get('cohesion', 15.0),
            surcharge_load=params.get('surcharge_load', 10.0),
            seismic_coefficient=params.get('seismic_coefficient', 0.1),
            safety_factor_sliding=params.get('safety_factor_sliding', 1.5),
            safety_factor_overturning=params.get('safety_factor_overturning', 2.0),
            bearing_capacity=params.get('bearing_capacity', 450.0)
        )
        
        # Calculate forces
        forces = self._calculate_forces(stability_params)
        
        # Overturning analysis
        overturning_results = self._analyze_overturning(stability_params, forces)
        
        # Sliding analysis
        sliding_results = self._analyze_sliding(stability_params, forces)
        
        # Bearing pressure analysis
        bearing_results = self._analyze_bearing_pressure(stability_params, forces)
        
        # Overall stability check
        overall_status = self._determine_overall_status(overturning_results, sliding_results, bearing_results)
        
        return {
            'forces': forces,
            'overturning_analysis': overturning_results,
            'sliding_analysis': sliding_results,
            'bearing_analysis': bearing_results,
            'overall_status': overall_status,
            'overturning_factor': overturning_results['safety_factor'],
            'sliding_factor': sliding_results['safety_factor'],
            'max_soil_pressure': bearing_results['max_pressure'],
            'pressure_distribution': bearing_results['pressure_distribution'],
            'recommendations': self._generate_stability_recommendations(overturning_results, sliding_results, bearing_results)
        }
    
    def _extract_stability_params(self, excel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract stability parameters from Excel data"""
        
        # Default parameters based on PROJECT FILES examples
        params = {
            'structure_height': 6.5,
            'structure_width': 7.0,
            'concrete_density': 24.0,
            'soil_density': 18.0,
            'water_density': 10.0,
            'angle_of_friction': 30.0,
            'cohesion': 15.0,
            'surcharge_load': 10.0,
            'seismic_coefficient': 0.1,
            'safety_factor_sliding': 1.5,
            'safety_factor_overturning': 2.0,
            'bearing_capacity': 450.0
        }
        
        # Extract from Excel values where possible
        for sheet_name, sheet_data in excel_data.get('sheets', {}).items():
            values = sheet_data.get('values', {})
            
            for cell_ref, value in values.items():
                if isinstance(value, (int, float)):
                    # Heuristic matching for common stability parameters
                    if 15 <= value <= 30 and 'density' in str(cell_ref).lower():
                        if 20 <= value <= 30:
                            params['concrete_density'] = value
                        else:
                            params['soil_density'] = value
                    elif 200 <= value <= 800:  # Likely bearing capacity
                        params['bearing_capacity'] = value
                    elif 20 <= value <= 45:  # Likely friction angle
                        params['angle_of_friction'] = value
                    elif 3 <= value <= 12 and value != params['angle_of_friction']:  # Likely height/width
                        if value > 8:
                            params['structure_width'] = value
                        else:
                            params['structure_height'] = value
        
        return params
    
    def _calculate_forces(self, params: StabilityParameters) -> Dict[str, Any]:
        """Calculate all forces acting on the structure"""
        
        self.calculation_steps['force_calculation'] = {}
        
        # Dimensions (simplified rectangular section)
        H = params.structure_height
        B = params.structure_width
        
        # Self weight of structure (simplified as rectangular block)
        volume = H * B * 1.0  # Per meter length
        self_weight = volume * params.concrete_density
        
        self.calculation_steps['force_calculation']['self_weight'] = {
            'volume': volume,
            'unit_weight': params.concrete_density,
            'total_weight': self_weight,
            'location': B / 2  # Acting at center
        }
        
        # Earth pressure (active earth pressure - Rankine theory)
        phi_rad = math.radians(params.angle_of_friction)
        ka = (1 - math.sin(phi_rad)) / (1 + math.sin(phi_rad))  # Active earth pressure coefficient
        
        # Active pressure at base
        pa_base = ka * params.soil_density * H + ka * params.surcharge_load
        
        # Total active force
        active_force = 0.5 * ka * params.soil_density * H * H + ka * params.surcharge_load * H
        
        # Height of application of active force
        if params.surcharge_load > 0:
            h1 = (ka * params.soil_density * H * H * H / 3) / active_force
            h2 = (ka * params.surcharge_load * H * H / 2) / active_force
            active_force_height = h1 + h2
        else:
            active_force_height = H / 3
        
        self.calculation_steps['force_calculation']['active_earth_pressure'] = {
            'ka': ka,
            'pressure_at_base': pa_base,
            'total_force': active_force,
            'height_of_application': active_force_height
        }
        
        # Passive earth pressure (in front of structure, if applicable)
        kp = (1 + math.sin(phi_rad)) / (1 - math.sin(phi_rad))
        passive_force = 0.5 * kp * params.soil_density * (H / 3) * (H / 3)  # Assuming 1/3 height buried
        
        self.calculation_steps['force_calculation']['passive_earth_pressure'] = {
            'kp': kp,
            'total_force': passive_force,
            'height_of_application': H / 9
        }
        
        # Seismic forces (if applicable)
        seismic_horizontal = params.seismic_coefficient * self_weight
        seismic_height = H / 2  # Applied at center of gravity
        
        self.calculation_steps['force_calculation']['seismic_force'] = {
            'coefficient': params.seismic_coefficient,
            'horizontal_force': seismic_horizontal,
            'height_of_application': seismic_height
        }
        
        # Water pressure (if applicable)
        water_force = 0  # Assuming no water pressure for now
        
        # Summary of forces
        vertical_forces = {
            'self_weight': self_weight,
            'total': self_weight
        }
        
        horizontal_forces = {
            'active_earth_pressure': active_force,
            'seismic': seismic_horizontal,
            'passive_resistance': -passive_force,  # Negative as it opposes motion
            'total_destabilizing': active_force + seismic_horizontal,
            'total_stabilizing': passive_force
        }
        
        return {
            'vertical': vertical_forces,
            'horizontal': horizontal_forces,
            'detailed_forces': {
                'self_weight': {
                    'magnitude': self_weight,
                    'x_component': 0,
                    'y_component': self_weight,
                    'location_x': B / 2,
                    'location_y': 0
                },
                'active_earth_pressure': {
                    'magnitude': active_force,
                    'x_component': active_force,
                    'y_component': 0,
                    'location_x': B,
                    'location_y': active_force_height
                },
                'seismic_force': {
                    'magnitude': seismic_horizontal,
                    'x_component': seismic_horizontal,
                    'y_component': 0,
                    'location_x': B / 2,
                    'location_y': seismic_height
                },
                'passive_resistance': {
                    'magnitude': passive_force,
                    'x_component': -passive_force,
                    'y_component': 0,
                    'location_x': 0,
                    'location_y': H / 9
                }
            }
        }
    
    def _analyze_overturning(self, params: StabilityParameters, forces: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze overturning stability"""
        
        B = params.structure_width
        
        # Overturning moments (about toe)
        active_moment = forces['horizontal']['active_earth_pressure'] * (params.structure_height / 3)
        seismic_moment = forces['horizontal']['seismic'] * (params.structure_height / 2)
        
        total_overturning_moment = active_moment + seismic_moment
        
        # Resisting moments (about toe)
        self_weight_moment = forces['vertical']['self_weight'] * (B / 2)
        
        total_resisting_moment = self_weight_moment
        
        # Safety factor
        safety_factor = total_resisting_moment / max(total_overturning_moment, 1e-6)
        
        # Check against required safety factor
        is_safe = safety_factor >= params.safety_factor_overturning
        
        self.calculation_steps['overturning_analysis'] = {
            'overturning_moments': {
                'active_earth_pressure': active_moment,
                'seismic': seismic_moment,
                'total': total_overturning_moment
            },
            'resisting_moments': {
                'self_weight': self_weight_moment,
                'total': total_resisting_moment
            },
            'safety_factor': safety_factor,
            'required_safety_factor': params.safety_factor_overturning,
            'status': 'SAFE' if is_safe else 'UNSAFE'
        }
        
        return {
            'overturning_moment': total_overturning_moment,
            'resisting_moment': total_resisting_moment,
            'safety_factor': safety_factor,
            'required_safety_factor': params.safety_factor_overturning,
            'is_safe': is_safe,
            'status': 'SAFE' if is_safe else 'UNSAFE'
        }
    
    def _analyze_sliding(self, params: StabilityParameters, forces: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze sliding stability"""
        
        # Horizontal forces
        driving_force = forces['horizontal']['total_destabilizing']
        passive_resistance = abs(forces['horizontal']['passive_resistance'])
        
        # Friction resistance
        normal_force = forces['vertical']['total']
        friction_angle_rad = math.radians(params.angle_of_friction)
        friction_resistance = normal_force * math.tan(friction_angle_rad)
        
        # Cohesion resistance
        base_area = params.structure_width * 1.0  # Per meter length
        cohesion_resistance = params.cohesion * base_area
        
        # Total resisting force
        total_resistance = friction_resistance + cohesion_resistance + passive_resistance
        
        # Safety factor
        safety_factor = total_resistance / max(driving_force, 1e-6)
        
        # Check against required safety factor
        is_safe = safety_factor >= params.safety_factor_sliding
        
        self.calculation_steps['sliding_analysis'] = {
            'driving_forces': {
                'active_pressure': forces['horizontal']['active_earth_pressure'],
                'seismic': forces['horizontal']['seismic'],
                'total': driving_force
            },
            'resisting_forces': {
                'friction': friction_resistance,
                'cohesion': cohesion_resistance,
                'passive': passive_resistance,
                'total': total_resistance
            },
            'safety_factor': safety_factor,
            'required_safety_factor': params.safety_factor_sliding,
            'status': 'SAFE' if is_safe else 'UNSAFE'
        }
        
        return {
            'driving_force': driving_force,
            'resisting_force': total_resistance,
            'friction_resistance': friction_resistance,
            'cohesion_resistance': cohesion_resistance,
            'passive_resistance': passive_resistance,
            'safety_factor': safety_factor,
            'required_safety_factor': params.safety_factor_sliding,
            'is_safe': is_safe,
            'status': 'SAFE' if is_safe else 'UNSAFE'
        }
    
    def _analyze_bearing_pressure(self, params: StabilityParameters, forces: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze bearing pressure distribution"""
        
        B = params.structure_width
        
        # Vertical load
        V = forces['vertical']['total']
        
        # Moment about center of base
        overturning_moment = forces['horizontal']['active_earth_pressure'] * (params.structure_height / 3)
        seismic_moment = forces['horizontal']['seismic'] * (params.structure_height / 2)
        total_moment = overturning_moment + seismic_moment
        
        # Eccentricity
        e = total_moment / V
        
        # Check if resultant falls within middle third
        middle_third_limit = B / 6
        resultant_within_middle_third = e <= middle_third_limit
        
        # Pressure distribution
        if resultant_within_middle_third:
            # No tension, trapezoidal distribution
            q_max = (V / B) * (1 + 6 * e / B)
            q_min = (V / B) * (1 - 6 * e / B)
            tension_area = 0
        else:
            # Tension exists, triangular distribution
            effective_length = 3 * (B / 2 - e)
            q_max = 2 * V / effective_length
            q_min = 0
            tension_area = B - effective_length
        
        # Check against bearing capacity
        pressure_safe = q_max <= params.bearing_capacity
        
        # Pressure distribution coordinates
        x_coords = np.linspace(0, B, 11).tolist()
        pressures = []
        
        for x in x_coords:
            if resultant_within_middle_third:
                # Linear interpolation for trapezoidal distribution
                pressure = q_min + (q_max - q_min) * x / B
            else:
                # Triangular distribution
                if x <= effective_length:
                    pressure = q_max * (1 - x / effective_length)
                else:
                    pressure = 0  # Tension zone
            pressures.append(max(pressure, 0))  # No negative pressures shown
        
        self.calculation_steps['bearing_analysis'] = {
            'vertical_load': V,
            'moment': total_moment,
            'eccentricity': e,
            'middle_third_limit': middle_third_limit,
            'resultant_location': 'WITHIN_MIDDLE_THIRD' if resultant_within_middle_third else 'OUTSIDE_MIDDLE_THIRD',
            'pressure_distribution': {
                'max_pressure': q_max,
                'min_pressure': q_min,
                'tension_area': tension_area
            },
            'bearing_capacity_check': 'SAFE' if pressure_safe else 'UNSAFE'
        }
        
        return {
            'max_pressure': q_max,
            'min_pressure': q_min,
            'eccentricity': e,
            'tension_area': tension_area,
            'bearing_capacity': params.bearing_capacity,
            'pressure_safe': pressure_safe,
            'resultant_within_middle_third': resultant_within_middle_third,
            'pressure_distribution': {
                'x_coordinates': x_coords,
                'pressures': pressures
            },
            'status': 'SAFE' if pressure_safe and tension_area == 0 else 'UNSAFE'
        }
    
    def _determine_overall_status(self, overturning: Dict[str, Any], sliding: Dict[str, Any], 
                                  bearing: Dict[str, Any]) -> str:
        """Determine overall stability status"""
        
        checks = [
            overturning['is_safe'],
            sliding['is_safe'],
            bearing['pressure_safe']
        ]
        
        if all(checks):
            return 'STRUCTURALLY_STABLE'
        elif overturning['is_safe'] and sliding['is_safe']:
            return 'STABLE_BEARING_REVIEW'
        elif bearing['pressure_safe']:
            return 'BEARING_OK_STABILITY_REVIEW'
        else:
            return 'STABILITY_FAILURE'
    
    def _generate_stability_recommendations(self, overturning: Dict[str, Any], sliding: Dict[str, Any],
                                            bearing: Dict[str, Any]) -> List[str]:
        """Generate stability improvement recommendations"""
        
        recommendations = []
        
        # Overturning recommendations
        if not overturning['is_safe']:
            if overturning['safety_factor'] < 1.5:
                recommendations.append("CRITICAL: Increase base width or add counterweight to improve overturning resistance")
            else:
                recommendations.append("Increase base width slightly to meet overturning safety factor")
        
        # Sliding recommendations
        if not sliding['is_safe']:
            if sliding['safety_factor'] < 1.2:
                recommendations.append("CRITICAL: Provide shear key or increase base friction to prevent sliding")
            else:
                recommendations.append("Consider adding shear key or increasing base roughness")
        
        # Bearing pressure recommendations
        if not bearing['pressure_safe']:
            if bearing['max_pressure'] > bearing['bearing_capacity'] * 1.5:
                recommendations.append("CRITICAL: Soil bearing capacity exceeded - soil improvement or pile foundation required")
            else:
                recommendations.append("Increase base area or improve soil bearing capacity")
        
        if bearing['tension_area'] > 0:
            recommendations.append("Resultant outside middle third - consider increasing base width to eliminate tension")
        
        # General recommendations
        if all([overturning['is_safe'], sliding['is_safe'], bearing['pressure_safe']]):
            recommendations.append("Structure is stable - proceed with detailed design")
        
        recommendations.extend([
            "Verify soil parameters through detailed geotechnical investigation",
            "Consider dynamic analysis for seismic conditions",
            "Provide adequate drainage to prevent buildup of water pressure"
        ])
        
        return recommendations
    
    def _identify_stability_formulas(self, excel_data: Dict[str, Any]) -> Dict[str, str]:
        """Identify stability-related formulas from Excel data"""
        
        stability_formulas = {}
        
        stability_keywords = [
            'moment', 'overturning', 'sliding', 'pressure', 'factor',
            'safety', 'bearing', 'force', 'weight', 'earth', 'friction'
        ]
        
        for sheet_name, sheet_data in excel_data.get('sheets', {}).items():
            formulas = sheet_data.get('formulas', {})
            
            for cell_ref, formula in formulas.items():
                formula_lower = formula.lower()
                if any(keyword in formula_lower for keyword in stability_keywords):
                    stability_formulas[f"{sheet_name}!{cell_ref}"] = formula
        
        return stability_formulas

