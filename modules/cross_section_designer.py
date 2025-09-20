"""
Cross Section Designer Module
Based on cross-section design Excel sheets from PROJECT FILES
Implements bridge deck slab design with live load distribution
"""

import numpy as np
import pandas as pd
import math
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class LoadClass(Enum):
    CLASS_A = "Class A"
    CLASS_AA = "Class AA" 
    CLASS_70R = "Class 70R"
    CLASS_A_70R = "Class A + 70R"

@dataclass
class CrossSectionGeometry:
    """Cross section geometric parameters"""
    total_width: float           # Total bridge width
    carriageway_width: float     # Effective carriageway width
    footpath_width: float        # Footpath width (each side)
    crash_barrier_width: float   # Crash barrier width (each side)
    slab_thickness: float        # Main slab thickness
    wearing_coat_thickness: float # Wearing coat thickness
    edge_beam_width: float       # Edge beam width
    edge_beam_depth: float       # Edge beam depth

class CrossSectionDesigner:
    """Cross section design based on PROJECT FILES Excel formulas"""
    
    def __init__(self, project_data):
        self.project_data = project_data
        self.material_properties = self._initialize_material_properties()
        self.load_factors = self._initialize_load_factors()
        
    def _initialize_material_properties(self) -> Dict[str, float]:
        """Initialize material properties"""
        return {
            'fck': 25,           # N/mm² - Concrete grade
            'fy': 415,           # N/mm² - Steel grade
            'ec': 25000,         # N/mm² - Concrete modulus
            'es': 200000,        # N/mm² - Steel modulus
            'concrete_density': 25.0,  # kN/m³
            'steel_density': 78.5,     # kN/m³
            'wearing_coat_density': 22.0,  # kN/m³
            'gamma_c': 1.5,      # Partial safety factor for concrete
            'gamma_s': 1.15      # Partial safety factor for steel
        }
    
    def _initialize_load_factors(self) -> Dict[str, float]:
        """Initialize load factors"""
        return {
            'dead_load': 1.35,
            'live_load': 1.75,
            'wearing_coat': 1.35,
            'crash_barrier': 1.35
        }
    
    def design(self, design_params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform complete cross section design"""
        
        # Create geometry
        geometry = self._create_geometry(design_params)
        
        # Load analysis
        load_analysis = self._analyze_loads(geometry, design_params)
        
        # Moment and shear analysis
        force_analysis = self._analyze_forces(geometry, load_analysis, design_params)
        
        # Reinforcement design
        reinforcement = self._design_reinforcement(geometry, force_analysis)
        
        # Deflection check
        deflection = self._check_deflection(geometry, force_analysis, reinforcement)
        
        # Design status
        design_status = self._determine_design_status(force_analysis, reinforcement, deflection)
        
        return {
            'geometry': geometry.__dict__,
            'load_analysis': load_analysis,
            'force_analysis': force_analysis,
            'reinforcement': reinforcement,
            'deflection': deflection,
            'design_status': design_status,
            'total_width': geometry.total_width,
            'effective_depth': geometry.slab_thickness - 0.05,  # Assuming 50mm cover
            'max_moment': force_analysis.get('max_moment', 0),
            'max_shear': force_analysis.get('max_shear', 0),
            'steel_required': reinforcement.get('main_steel_required', 0),
            'deflection': deflection.get('calculated_deflection', 0)
        }
    
    def _create_geometry(self, params: Dict[str, Any]) -> CrossSectionGeometry:
        """Create cross section geometry"""
        
        carriageway_width = params.get('carriageway_width', 7.5)
        footpath_width = params.get('footpath_width', 1.0)
        crash_barrier_width = params.get('crash_barrier_width', 0.5)
        
        # Calculate total width
        total_width = carriageway_width + 2 * footpath_width + 2 * crash_barrier_width
        
        # Slab thickness
        slab_thickness = params.get('slab_thickness', 0.5)
        
        # Other dimensions
        wearing_coat_thickness = params.get('wearing_coat', 0.075)
        edge_beam_width = params.get('edge_beam_width', 0.5)
        edge_beam_depth = slab_thickness + 0.3  # 300mm additional depth
        
        return CrossSectionGeometry(
            total_width=total_width,
            carriageway_width=carriageway_width,
            footpath_width=footpath_width,
            crash_barrier_width=crash_barrier_width,
            slab_thickness=slab_thickness,
            wearing_coat_thickness=wearing_coat_thickness,
            edge_beam_width=edge_beam_width,
            edge_beam_depth=edge_beam_depth
        )
    
    def _analyze_loads(self, geometry: CrossSectionGeometry, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze all loads on cross section"""
        
        # Dead loads
        dead_loads = self._calculate_dead_loads(geometry)
        
        # Live loads
        live_loads = self._calculate_live_loads(geometry, params)
        
        # Factored loads
        factored_loads = self._calculate_factored_loads(dead_loads, live_loads)
        
        # Load distribution
        load_distribution = self._calculate_load_distribution(geometry, factored_loads)
        
        return {
            'dead_loads': dead_loads,
            'live_loads': live_loads,
            'factored_loads': factored_loads,
            'load_distribution': load_distribution,
            'self_weight': dead_loads['self_weight'],
            'wearing_coat': dead_loads['wearing_coat'],
            'crash_barrier': dead_loads['crash_barrier'],
            'total_dead_load': dead_loads['total_dead_load'],
            'live_load_intensity': live_loads['design_live_load'],
            'impact_factor': live_loads['impact_factor'],
            'total_live_load': live_loads['total_live_load'],
            'factored_dl': factored_loads['factored_dead'],
            'factored_ll': factored_loads['factored_live'],
            'total_design_load': factored_loads['total_factored']
        }
    
    def _calculate_dead_loads(self, geometry: CrossSectionGeometry) -> Dict[str, float]:
        """Calculate dead loads"""
        
        # Self weight of slab
        slab_volume_per_m = geometry.slab_thickness * geometry.total_width * 1.0
        self_weight = slab_volume_per_m * self.material_properties['concrete_density']
        
        # Wearing coat
        wearing_coat_area = geometry.carriageway_width * 1.0  # Only on carriageway
        wearing_coat_load = wearing_coat_area * geometry.wearing_coat_thickness * \
                           self.material_properties['wearing_coat_density']
        
        # Crash barriers (both sides)
        crash_barrier_load = 2 * 3.0  # kN/m (typical 3 kN/m per barrier)
        
        # Footpath load (including railings)
        footpath_load = 2 * geometry.footpath_width * 1.5  # kN/m (1.5 kN/m² for footpath)
        
        # Edge beams
        edge_beam_volume = 2 * geometry.edge_beam_width * geometry.edge_beam_depth * 1.0
        edge_beam_load = edge_beam_volume * self.material_properties['concrete_density']
        
        # Utilities and services
        utilities_load = 1.5  # kN/m
        
        total_dead_load = (self_weight + wearing_coat_load + crash_barrier_load + 
                          footpath_load + edge_beam_load + utilities_load)
        
        return {
            'self_weight': self_weight,
            'wearing_coat': wearing_coat_load,
            'crash_barrier': crash_barrier_load,
            'footpath': footpath_load,
            'edge_beam': edge_beam_load,
            'utilities': utilities_load,
            'total_dead_load': total_dead_load,
            'dead_load_per_sqm': total_dead_load / geometry.total_width
        }
    
    def _calculate_live_loads(self, geometry: CrossSectionGeometry, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate live loads based on IRC specifications"""
        
        load_class = params.get('live_load_class', 'Class A')
        impact_factor = params.get('impact_factor', 0.25)
        
        # Effective carriageway width for load calculation
        effective_width = min(geometry.carriageway_width, 7.5)  # Max 7.5m for Class A
        
        if load_class == "Class A":
            # IRC Class A loading
            udl_intensity = 5.0  # kN/m²
            concentrated_load = 27.0  # kN per wheel
            contact_area = 0.3 * 0.3  # m²
            
        elif load_class == "Class AA":
            # IRC Class AA loading
            udl_intensity = 8.0  # kN/m²
            concentrated_load = 40.0  # kN per wheel
            contact_area = 0.3 * 0.3  # m²
            
        elif load_class == "Class 70R":
            # IRC Class 70R tracked vehicle
            track_load = 700.0  # kN total
            track_length = 3.6  # m
            track_width = 0.84  # m
            udl_intensity = track_load / (track_length * track_width)
            concentrated_load = track_load / 2  # Two tracks
            contact_area = track_length * track_width / 2
            
        else:  # Class A + 70R
            # Take the maximum of Class A and 70R
            udl_intensity = max(5.0, 700.0 / (3.6 * 0.84))
            concentrated_load = max(27.0, 350.0)
            contact_area = 0.3 * 0.3
        
        # Total live load over effective width
        total_udl = udl_intensity * effective_width
        
        # Design live load including impact
        design_live_load = total_udl * (1 + impact_factor)
        
        # For moment calculation, also consider concentrated load
        concentrated_moment_effect = self._calculate_concentrated_load_effect(
            concentrated_load, contact_area, geometry)
        
        return {
            'load_class': load_class,
            'udl_intensity': udl_intensity,
            'concentrated_load': concentrated_load,
            'effective_width': effective_width,
            'total_udl': total_udl,
            'impact_factor': impact_factor,
            'design_live_load': design_live_load,
            'total_live_load': design_live_load,
            'concentrated_moment_effect': concentrated_moment_effect
        }
    
    def _calculate_concentrated_load_effect(self, concentrated_load: float, contact_area: float,
                                          geometry: CrossSectionGeometry) -> float:
        """Calculate effect of concentrated load"""
        
        # Load distribution through slab thickness
        dispersion_slope = 2  # 45 degree dispersion
        effective_area = contact_area + 4 * geometry.slab_thickness * \
                        (geometry.slab_thickness * dispersion_slope)
        
        # Distributed pressure
        distributed_pressure = concentrated_load / effective_area
        
        return distributed_pressure
    
    def _calculate_factored_loads(self, dead_loads: Dict[str, float], live_loads: Dict[str, float]) -> Dict[str, float]:
        """Calculate factored loads"""
        
        factored_dead = dead_loads['total_dead_load'] * self.load_factors['dead_load']
        factored_live = live_loads['total_live_load'] * self.load_factors['live_load']
        
        total_factored = factored_dead + factored_live
        
        return {
            'factored_dead': factored_dead,
            'factored_live': factored_live,
            'total_factored': total_factored
        }
    
    def _calculate_load_distribution(self, geometry: CrossSectionGeometry, 
                                   factored_loads: Dict[str, float]) -> Dict[str, Any]:
        """Calculate load distribution across bridge width"""
        
        # Create distribution points across width
        num_points = 21
        x_coordinates = np.linspace(0, geometry.total_width, num_points).tolist()
        
        # Dead load distribution (uniform)
        dead_loads = [factored_loads['factored_dead'] / geometry.total_width] * num_points
        
        # Live load distribution (varies across carriageway)
        live_loads = []
        carriageway_start = geometry.crash_barrier_width + geometry.footpath_width
        carriageway_end = carriageway_start + geometry.carriageway_width
        
        for x in x_coordinates:
            if carriageway_start <= x <= carriageway_end:
                # Full live load on carriageway
                live_load = factored_loads['factored_live'] / geometry.carriageway_width
            else:
                # No vehicular live load on footpath/barriers
                live_load = 0.0
            live_loads.append(live_load)
        
        return {
            'x_coordinates': x_coordinates,
            'dead_loads': dead_loads,
            'live_loads': live_loads,
            'total_loads': [d + l for d, l in zip(dead_loads, live_loads)]
        }
    
    def _analyze_forces(self, geometry: CrossSectionGeometry, load_analysis: Dict[str, Any],
                       params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze moments and shears"""
        
        # Get span length
        span_length = getattr(self.project_data, 'span_length', 10.0)
        
        # Total factored load per meter length
        total_load = load_analysis['factored_loads']['total_factored']
        
        # For simply supported slab
        max_moment = total_load * span_length**2 / 8  # kN-m per meter width
        max_shear = total_load * span_length / 2      # kN per meter width
        
        # Live load positioning for maximum effect
        ll_max_moment = self._calculate_live_load_max_moment(geometry, load_analysis, span_length)
        
        # Consider concentrated load effects
        conc_load_moment = load_analysis['live_loads'].get('concentrated_moment_effect', 0)
        
        # Final design moments
        design_moment = max(max_moment, ll_max_moment) + conc_load_moment
        design_shear = max_shear  # Conservative for shear
        
        return {
            'span_length': span_length,
            'total_load_per_m': total_load,
            'max_moment': design_moment,
            'max_shear': design_shear,
            'live_load_max_moment': ll_max_moment,
            'concentrated_load_moment': conc_load_moment,
            'moment_distribution': self._calculate_moment_distribution(total_load, span_length),
            'shear_distribution': self._calculate_shear_distribution(total_load, span_length)
        }
    
    def _calculate_live_load_max_moment(self, geometry: CrossSectionGeometry, 
                                       load_analysis: Dict[str, Any], span_length: float) -> float:
        """Calculate maximum moment due to live load positioning"""
        
        live_load = load_analysis['live_loads']['design_live_load']
        factored_ll = live_load * self.load_factors['live_load']
        
        # For IRC loading, live load should be positioned for maximum moment
        # Using influence line approach (simplified)
        max_influence = span_length / 4  # Maximum ordinate of influence line
        
        return factored_ll * max_influence
    
    def _calculate_moment_distribution(self, load: float, span: float) -> Dict[str, List[float]]:
        """Calculate moment distribution along span"""
        
        num_points = 21
        x_positions = np.linspace(0, span, num_points)
        moments = []
        
        for x in x_positions:
            # Moment for uniformly distributed load
            moment = load * x * (span - x) / 2
            moments.append(moment)
        
        return {
            'x_positions': x_positions.tolist(),
            'moments': moments
        }
    
    def _calculate_shear_distribution(self, load: float, span: float) -> Dict[str, List[float]]:
        """Calculate shear distribution along span"""
        
        num_points = 21
        x_positions = np.linspace(0, span, num_points)
        shears = []
        
        for x in x_positions:
            # Shear for uniformly distributed load
            shear = load * (span/2 - x)
            shears.append(shear)
        
        return {
            'x_positions': x_positions.tolist(),
            'shears': shears
        }
    
    def _design_reinforcement(self, geometry: CrossSectionGeometry, force_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Design reinforcement for cross section"""
        
        # Main flexural reinforcement
        main_reinforcement = self._design_main_flexural_reinforcement(geometry, force_analysis)
        
        # Distribution reinforcement
        distribution_reinforcement = self._design_distribution_reinforcement(geometry)
        
        # Shear reinforcement
        shear_reinforcement = self._design_shear_reinforcement(geometry, force_analysis)
        
        # Reinforcement layout
        rebar_layout = self._create_reinforcement_layout(geometry, main_reinforcement, distribution_reinforcement)
        
        return {
            'main_reinforcement': main_reinforcement,
            'distribution_reinforcement': distribution_reinforcement,
            'shear_reinforcement': shear_reinforcement,
            'rebar_layout': rebar_layout,
            'main_steel_required': main_reinforcement['required_area'],
            'main_steel_provided': main_reinforcement['provided_details'],
            'dist_steel_required': distribution_reinforcement['required_area'],
            'dist_steel_provided': distribution_reinforcement['provided_details'],
            'shear_check': shear_reinforcement['shear_check'],
            'stirrups_required': shear_reinforcement.get('stirrups_required', 'Not required')
        }
    
    def _design_main_flexural_reinforcement(self, geometry: CrossSectionGeometry, force_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Design main flexural reinforcement"""
        
        # Design moment
        moment = force_analysis['max_moment']  # kN-m per meter width
        
        # Section properties
        b = 1000  # mm (per meter width)
        d = (geometry.slab_thickness - 0.05) * 1000  # mm (effective depth)
        
        # Material properties
        fck = self.material_properties['fck']
        fy = self.material_properties['fy']
        
        # Limiting moment
        xu_max = 0.48 * d  # Maximum neutral axis depth
        Mu_lim = 0.36 * fck * b * xu_max * (d - 0.42 * xu_max) / 1e6  # kN-m
        
        if moment <= Mu_lim:
            # Singly reinforced section
            # Using simplified formula: Ast = M / (0.87 * fy * 0.9 * d)
            required_area = (moment * 1e6) / (0.87 * fy * 0.9 * d)  # mm²
            compression_steel = 0
        else:
            # Doubly reinforced section (rarely needed for slabs)
            required_area = (Mu_lim * 1e6) / (0.87 * fy * 0.9 * d)
            compression_steel = ((moment - Mu_lim) * 1e6) / (0.87 * fy * (d - 50))
        
        # Minimum steel requirement (0.12% for slabs)
        min_area = 0.12 * b * geometry.slab_thickness * 1000 / 100  # mm²
        
        # Maximum steel requirement (4% of gross area)
        max_area = 4.0 * b * geometry.slab_thickness * 1000 / 100  # mm²
        
        # Provided area
        provided_area = max(required_area, min_area)
        provided_area = min(provided_area, max_area)
        
        # Bar selection
        bar_details = self._select_bars(provided_area, b)
        
        return {
            'design_moment': moment,
            'required_area': required_area,
            'minimum_area': min_area,
            'provided_area': provided_area,
            'compression_steel': compression_steel,
            'bar_details': bar_details,
            'provided_details': bar_details['bar_description'],
            'steel_ratio': provided_area / (b * d) * 100
        }
    
    def _design_distribution_reinforcement(self, geometry: CrossSectionGeometry) -> Dict[str, Any]:
        """Design distribution reinforcement"""
        
        # Distribution steel is typically 20% of main steel or minimum 0.12%
        main_steel_area = 1500  # Assumed mm² per meter (will be updated)
        
        # Distribution steel requirement
        dist_percentage = max(0.2, 0.12)  # 20% of main steel or 0.12% minimum
        
        b = 1000  # mm (per meter width)
        required_area = max(
            dist_percentage * main_steel_area,
            0.12 * b * geometry.slab_thickness * 1000 / 100
        )
        
        # Bar selection for distribution steel
        bar_details = self._select_bars(required_area, b, max_spacing=250)
        
        return {
            'required_area': required_area,
            'provided_area': bar_details['total_area'],
            'bar_details': bar_details,
            'provided_details': bar_details['bar_description']
        }
    
    def _design_shear_reinforcement(self, geometry: CrossSectionGeometry, force_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Design shear reinforcement"""
        
        # Design shear force
        shear_force = force_analysis['max_shear']  # kN per meter
        
        # Section properties
        b = 1000  # mm (per meter width)
        d = (geometry.slab_thickness - 0.05) * 1000  # mm
        
        # Shear stress
        tau_v = (shear_force * 1000) / (b * d)  # N/mm²
        
        # Permissible shear stress for concrete
        fck = self.material_properties['fck']
        tau_c = 0.62 * math.sqrt(fck)  # Simplified formula
        
        if tau_v <= tau_c:
            shear_check = "SAFE - No shear reinforcement required"
            stirrups_required = None
        else:
            shear_check = "Shear reinforcement required"
            # Design stirrups (simplified)
            asv_sv = (tau_v - tau_c) * b / (0.87 * self.material_properties['fy'])
            stirrups_required = f"8mm @ {min(300, int(50.3 / asv_sv))}mm c/c"  # Assuming 8mm stirrups
        
        return {
            'design_shear': shear_force,
            'shear_stress': tau_v,
            'permissible_shear': tau_c,
            'shear_check': shear_check,
            'stirrups_required': stirrups_required
        }
    
    def _select_bars(self, required_area: float, width: float, max_spacing: float = 300) -> Dict[str, Any]:
        """Select appropriate bar size and spacing"""
        
        # Available bar sizes and their areas
        bar_data = {
            10: 78.5,   # mm²
            12: 113.1,  # mm²
            16: 201.1,  # mm²
            20: 314.2,  # mm²
            25: 490.9   # mm²
        }
        
        best_option = None
        min_waste = float('inf')
        
        for bar_size, bar_area in bar_data.items():
            # Calculate number of bars required
            num_bars = required_area / bar_area
            spacing = width / num_bars
            
            # Check if spacing is practical
            if 100 <= spacing <= max_spacing:
                num_bars_provided = int(width / spacing) + 1
                total_area_provided = num_bars_provided * bar_area
                waste = total_area_provided - required_area
                
                if waste < min_waste:
                    min_waste = waste
                    best_option = {
                        'bar_size': bar_size,
                        'bar_area': bar_area,
                        'spacing': spacing,
                        'num_bars': num_bars_provided,
                        'total_area': total_area_provided,
                        'bar_description': f"{bar_size}mm @ {int(spacing)}mm c/c"
                    }
        
        # Fallback if no suitable option found
        if best_option is None:
            best_option = {
                'bar_size': 16,
                'bar_area': 201.1,
                'spacing': 200,
                'num_bars': int(width / 200),
                'total_area': int(width / 200) * 201.1,
                'bar_description': "16mm @ 200mm c/c"
            }
        
        return best_option
    
    def _create_reinforcement_layout(self, geometry: CrossSectionGeometry, 
                                   main_rebar: Dict[str, Any], dist_rebar: Dict[str, Any]) -> Dict[str, Any]:
        """Create reinforcement layout details"""
        
        return {
            'main_direction': 'Longitudinal (parallel to traffic)',
            'distribution_direction': 'Transverse (perpendicular to traffic)',
            'main_bars_bottom': main_rebar['bar_description'],
            'distribution_bars_top': dist_rebar['bar_description'],
            'clear_cover': '50mm all around',
            'lap_length': f"{40 * main_rebar['bar_size']}mm for main bars",
            'anchorage_length': f"{30 * main_rebar['bar_size']}mm"
        }
    
    def _check_deflection(self, geometry: CrossSectionGeometry, force_analysis: Dict[str, Any],
                         reinforcement: Dict[str, Any]) -> Dict[str, Any]:
        """Check deflection of slab"""
        
        # Basic deflection calculation for simply supported slab
        span = force_analysis['span_length']
        moment = force_analysis['max_moment']
        
        # Section properties
        b = geometry.total_width * 1000  # mm
        d = (geometry.slab_thickness - 0.05) * 1000  # mm
        
        # Moment of inertia (simplified, assuming cracked section)
        Ig = b * (geometry.slab_thickness * 1000)**3 / 12  # Gross moment of inertia
        Ie = 0.4 * Ig  # Effective moment of inertia (simplified)
        
        # Deflection calculation
        E = self.material_properties['ec']  # N/mm²
        total_load = force_analysis['total_load_per_m']  # kN/m
        
        # For uniformly distributed load: δ = 5wL⁴/(384EI)
        deflection = (5 * total_load * 1000 * (span * 1000)**4) / (384 * E * Ie)  # mm
        
        # Deflection limits
        deflection_limit = span * 1000 / 250  # L/250 for highway bridges
        service_limit = span * 1000 / 350     # L/350 for serviceability
        
        return {
            'calculated_deflection': deflection,
            'deflection_limit': deflection_limit,
            'service_limit': service_limit,
            'deflection_ratio': deflection / deflection_limit,
            'deflection_check': 'PASS' if deflection <= deflection_limit else 'FAIL',
            'serviceability_check': 'PASS' if deflection <= service_limit else 'FAIL'
        }
    
    def _determine_design_status(self, force_analysis: Dict[str, Any], 
                                reinforcement: Dict[str, Any], deflection: Dict[str, Any]) -> str:
        """Determine overall design status"""
        
        checks = [
            reinforcement['main_reinforcement']['provided_area'] >= reinforcement['main_reinforcement']['required_area'],
            reinforcement['shear_reinforcement']['shear_check'] in ['SAFE - No shear reinforcement required', 'Shear reinforcement required'],
            deflection['deflection_check'] == 'PASS'
        ]
        
        if all(checks):
            return 'SAFE'
        else:
            return 'NEEDS_REVISION'

