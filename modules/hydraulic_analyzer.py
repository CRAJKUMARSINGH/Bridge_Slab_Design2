"""
Hydraulic Analyzer Module
Based on hydraulic calculation Excel sheets from PROJECT FILES
Implements Lacey's Regime Theory, Afflux calculations, and Scour analysis
"""

import numpy as np
import pandas as pd
import math
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

@dataclass
class HydraulicParameters:
    """Hydraulic design parameters from Excel sheets"""
    discharge: float  # Q in cumecs
    hfl: float  # High Flood Level in m
    bed_slope: str  # Bed slope as "1 in X"
    manning_n: float  # Manning's roughness coefficient
    silt_factor: float  # Lacey's silt factor
    design_velocity: float  # Design velocity in m/s
    bridge_opening: float  # Total bridge opening in m
    afflux_limit: float  # Allowable afflux in m

class HydraulicAnalyzer:
    """Hydraulic analysis based on PROJECT FILES Excel formulas"""
    
    def __init__(self, project_data):
        self.project_data = project_data
        self.calculations = {}
        
    def analyze(self, hydraulic_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform complete hydraulic analysis"""
        
        params = HydraulicParameters(
            discharge=hydraulic_data['discharge'],
            hfl=hydraulic_data['hfl'],
            bed_slope=hydraulic_data['bed_slope'],
            manning_n=hydraulic_data['manning_n'],
            silt_factor=hydraulic_data['silt_factor'],
            design_velocity=hydraulic_data['design_velocity'],
            bridge_opening=hydraulic_data['bridge_opening'],
            afflux_limit=hydraulic_data['afflux_limit']
        )
        
        # Lacey's Regime Analysis
        regime_results = self._lacey_regime_analysis(params)
        
        # Afflux Calculation
        afflux_results = self._calculate_afflux(params, regime_results)
        
        # Scour Analysis
        scour_results = self._calculate_scour(params, regime_results)
        
        # Waterway Adequacy
        adequacy_results = self._check_waterway_adequacy(params, regime_results, afflux_results)
        
        # Pier spacing optimization
        pier_results = self._optimize_pier_spacing(params, regime_results)
        
        # Generate water surface profile
        profile_results = self._generate_water_profile(params, regime_results)
        
        # Overall status
        overall_status = self._determine_overall_status(afflux_results, adequacy_results)
        
        return {
            'regime_analysis': regime_results,
            'afflux_analysis': afflux_results,
            'scour_analysis': scour_results,
            'waterway_adequacy': adequacy_results,
            'pier_optimization': pier_results,
            'water_profile': profile_results,
            'status': overall_status,
            'regime_width': regime_results['regime_width'],
            'effective_waterway': regime_results['regime_width'],
            'afflux': afflux_results['calculated_afflux'],
            'scour_depth': scour_results['design_scour_depth'],
            'pier_spacing': pier_results['recommended_spacing'],
            'approach_velocity': regime_results['regime_velocity'],
            'bridge_velocity': afflux_results['bridge_velocity'],
            'regime_depth': regime_results['regime_depth'],
            'regime_velocity': regime_results['regime_velocity'],
            'foundation_level': scour_results['required_foundation_level']
        }
    
    def _lacey_regime_analysis(self, params: HydraulicParameters) -> Dict[str, float]:
        """Lacey's Regime Theory calculations from Excel formulas"""
        
        Q = params.discharge
        f = params.silt_factor
        
        # Lacey's formulas from Excel sheets
        # Regime width: Wr = 4.75 * sqrt(Q)
        regime_width = 4.75 * math.sqrt(Q)
        
        # Regime depth: Dr = 0.473 * (Q/f)^(1/3)
        regime_depth = 0.473 * ((Q / f) ** (1/3))
        
        # Regime velocity: Vr = (f * Dr)^0.5 / 1.35
        regime_velocity = math.sqrt(f * regime_depth) / 1.35
        
        # Alternative regime velocity: Vr = 1.17 * sqrt(f)
        regime_velocity_alt = 1.17 * math.sqrt(f)
        
        # Use the more conservative (lower) velocity
        regime_velocity = min(regime_velocity, regime_velocity_alt)
        
        # Check consistency: Q = Wr * Dr * Vr
        calculated_discharge = regime_width * regime_depth * regime_velocity
        discharge_error = abs((calculated_discharge - Q) / Q) * 100
        
        # Regime slope calculation
        # Sr = f^5/3 / (3340 * Q^1/6)
        regime_slope = (f ** (5/3)) / (3340 * (Q ** (1/6)))
        
        # Wetted perimeter
        wetted_perimeter = regime_width + 2 * regime_depth
        
        # Hydraulic radius
        hydraulic_radius = (regime_width * regime_depth) / wetted_perimeter
        
        return {
            'regime_width': regime_width,
            'regime_depth': regime_depth,
            'regime_velocity': regime_velocity,
            'regime_slope': regime_slope,
            'hydraulic_radius': hydraulic_radius,
            'wetted_perimeter': wetted_perimeter,
            'calculated_discharge': calculated_discharge,
            'discharge_error_percent': discharge_error,
            'regime_area': regime_width * regime_depth
        }
    
    def _calculate_afflux(self, params: HydraulicParameters, regime: Dict[str, float]) -> Dict[str, float]:
        """Calculate afflux using Molesworth's and other methods"""
        
        Q = params.discharge
        bridge_opening = params.bridge_opening
        regime_width = regime['regime_width']
        regime_velocity = regime['regime_velocity']
        
        # Approach velocity (upstream of bridge)
        approach_area = regime['regime_area']
        approach_velocity = Q / approach_area
        
        # Bridge section velocity
        # Assuming same depth at bridge section initially
        bridge_area = bridge_opening * regime['regime_depth']
        bridge_velocity = Q / bridge_area
        
        # Afflux calculation methods
        
        # Method 1: Molesworth's formula
        # h = (K * Q^2) / (2g * C^2 * W^2)
        # where K = coefficient (1.5 to 2.0), C = coefficient of discharge (0.95)
        K = 1.8  # Coefficient for bridge with piers
        C = 0.95  # Coefficient of discharge
        g = 9.81  # Acceleration due to gravity
        
        molesworth_afflux = (K * (Q ** 2)) / (2 * g * (C ** 2) * (bridge_opening ** 2))
        
        # Method 2: Energy equation
        # h = (V2^2 - V1^2) / (2g)
        energy_afflux = ((bridge_velocity ** 2) - (approach_velocity ** 2)) / (2 * g)
        
        # Method 3: Empirical formula for Indian conditions
        # h = 0.006 * (Q / W)^1.33
        empirical_afflux = 0.006 * ((Q / bridge_opening) ** 1.33)
        
        # Method 4: Bradley's formula
        # h = K * V^2 / (2g) where V is approach velocity
        bradley_k = 0.3  # Coefficient for multiple span bridges
        bradley_afflux = bradley_k * (approach_velocity ** 2) / (2 * g)
        
        # Take the maximum of calculated afflux values for safety
        calculated_afflux = max(molesworth_afflux, energy_afflux, empirical_afflux, bradley_afflux)
        
        # Waterway ratio
        waterway_ratio = bridge_opening / regime_width
        
        # Linear waterway
        linear_waterway = regime_width
        
        # Check against allowable afflux
        afflux_acceptable = calculated_afflux <= params.afflux_limit
        
        return {
            'approach_velocity': approach_velocity,
            'bridge_velocity': bridge_velocity,
            'molesworth_afflux': molesworth_afflux,
            'energy_afflux': energy_afflux,
            'empirical_afflux': empirical_afflux,
            'bradley_afflux': bradley_afflux,
            'calculated_afflux': calculated_afflux,
            'allowable_afflux': params.afflux_limit,
            'afflux_acceptable': afflux_acceptable,
            'waterway_ratio': waterway_ratio,
            'linear_waterway': linear_waterway,
            'bridge_opening': bridge_opening
        }
    
    def _calculate_scour(self, params: HydraulicParameters, regime: Dict[str, float]) -> Dict[str, float]:
        """Calculate scour depth using various methods"""
        
        # Design discharge and regime parameters
        Q = params.discharge
        f = params.silt_factor
        regime_depth = regime['regime_depth']
        regime_velocity = regime['regime_velocity']
        
        # Method 1: Lacey's scour formula
        # Rs = 0.473 * (q^2/f)^1/3
        # where q = discharge per unit width
        q = Q / regime['regime_width']
        lacey_scour = 0.473 * ((q ** 2 / f) ** (1/3))
        
        # Method 2: Blench's formula for regime scour
        # Rs = 1.35 * (Q/f)^1/3
        blench_scour = 1.35 * ((Q / f) ** (1/3))
        
        # Method 3: IRC recommended formula
        # Rs = 2.0 * R * (V/Vc)^2
        # where R = regime depth, V = velocity, Vc = critical velocity
        critical_velocity = 1.17 * math.sqrt(f)  # Lacey's critical velocity
        if regime_velocity > critical_velocity:
            irc_scour = 2.0 * regime_depth * ((regime_velocity / critical_velocity) ** 2)
        else:
            irc_scour = regime_depth  # No additional scour
        
        # Method 4: Inglis-Poona formula
        # Rs = 1.27 * (q/f^0.5)^0.725
        inglis_scour = 1.27 * ((q / math.sqrt(f)) ** 0.725)
        
        # Design scour depth (take maximum for safety)
        design_scour_depth = max(lacey_scour, blench_scour, irc_scour, inglis_scour)
        
        # Add safety factor
        safety_factor = 1.5  # 50% additional safety
        design_scour_with_safety = design_scour_depth * safety_factor
        
        # Foundation level calculation
        # Foundation should be below HFL - Design scour depth
        required_foundation_level = params.hfl - design_scour_with_safety
        
        # Minimum foundation depth below natural bed
        natural_bed_level = params.hfl - regime_depth
        min_foundation_depth = 2.0  # Minimum 2m below natural bed
        absolute_min_foundation = natural_bed_level - min_foundation_depth
        
        # Final foundation level (most conservative)
        final_foundation_level = min(required_foundation_level, absolute_min_foundation)
        
        return {
            'lacey_scour': lacey_scour,
            'blench_scour': blench_scour,
            'irc_scour': irc_scour,
            'inglis_scour': inglis_scour,
            'design_scour_depth': design_scour_depth,
            'design_scour_with_safety': design_scour_with_safety,
            'safety_factor': safety_factor,
            'required_foundation_level': required_foundation_level,
            'natural_bed_level': natural_bed_level,
            'final_foundation_level': final_foundation_level,
            'critical_velocity': critical_velocity
        }
    
    def _check_waterway_adequacy(self, params: HydraulicParameters, regime: Dict[str, float], 
                                 afflux: Dict[str, float]) -> Dict[str, Any]:
        """Check adequacy of provided waterway"""
        
        regime_width = regime['regime_width']
        bridge_opening = params.bridge_opening
        calculated_afflux = afflux['calculated_afflux']
        allowable_afflux = params.afflux_limit
        
        # Waterway adequacy checks
        checks = {
            'waterway_ratio_check': {
                'provided_ratio': bridge_opening / regime_width,
                'minimum_required': 0.8,  # Minimum 80% of regime width
                'status': 'PASS' if bridge_opening / regime_width >= 0.8 else 'FAIL'
            },
            'afflux_check': {
                'calculated_afflux': calculated_afflux,
                'allowable_afflux': allowable_afflux,
                'status': 'PASS' if calculated_afflux <= allowable_afflux else 'FAIL'
            },
            'velocity_check': {
                'bridge_velocity': afflux['bridge_velocity'],
                'maximum_allowable': params.design_velocity,
                'status': 'PASS' if afflux['bridge_velocity'] <= params.design_velocity else 'FAIL'
            }
        }
        
        # Overall adequacy
        all_checks_pass = all(check['status'] == 'PASS' for check in checks.values())
        
        # Recommendations
        recommendations = []
        
        if not checks['waterway_ratio_check']['status'] == 'PASS':
            required_opening = regime_width * 0.8
            recommendations.append(f"Increase bridge opening to at least {required_opening:.1f} m")
        
        if not checks['afflux_check']['status'] == 'PASS':
            recommendations.append("Reduce afflux by increasing bridge opening or providing training works")
        
        if not checks['velocity_check']['status'] == 'PASS':
            recommendations.append("Reduce velocity by increasing waterway area")
        
        if all_checks_pass:
            recommendations.append("Waterway is adequate for the given discharge")
        
        return {
            'adequacy_checks': checks,
            'overall_adequacy': 'ADEQUATE' if all_checks_pass else 'INADEQUATE',
            'recommendations': recommendations,
            'required_minimum_opening': regime_width * 0.8
        }
    
    def _optimize_pier_spacing(self, params: HydraulicParameters, regime: Dict[str, float]) -> Dict[str, float]:
        """Optimize pier spacing for hydraulic efficiency"""
        
        bridge_opening = params.bridge_opening
        total_span_length = getattr(self.project_data, 'span_length', 10.0) * getattr(self.project_data, 'num_spans', 3)
        
        # Typical pier width (assumed)
        pier_width = 1.5  # meters
        
        # Calculate number of piers based on spans
        num_spans = getattr(self.project_data, 'num_spans', 3)
        num_piers = num_spans - 1 if num_spans > 1 else 0
        
        # Effective opening (total opening - pier widths)
        effective_opening = bridge_opening - (num_piers * pier_width)
        
        # Recommended pier spacing for hydraulic efficiency
        if num_spans > 1:
            recommended_spacing = effective_opening / num_spans
        else:
            recommended_spacing = effective_opening
        
        # Check against hydraulic requirements
        # Minimum spacing = 0.8 * regime_width / num_spans
        min_hydraulic_spacing = 0.8 * regime['regime_width'] / num_spans if num_spans > 0 else 0
        
        # Structural minimum (based on span/depth ratio)
        span_depth_ratio = 15  # Typical for slab bridges
        slab_depth = recommended_spacing / span_depth_ratio
        structural_min_spacing = slab_depth * span_depth_ratio
        
        # Final recommendation
        final_spacing = max(recommended_spacing, min_hydraulic_spacing, structural_min_spacing)
        
        return {
            'total_bridge_length': total_span_length,
            'num_piers': num_piers,
            'pier_width': pier_width,
            'effective_opening': effective_opening,
            'recommended_spacing': recommended_spacing,
            'min_hydraulic_spacing': min_hydraulic_spacing,
            'structural_min_spacing': structural_min_spacing,
            'final_recommended_spacing': final_spacing,
            'spacing_adequacy': 'ADEQUATE' if final_spacing <= recommended_spacing * 1.1 else 'REVIEW_REQUIRED'
        }
    
    def _generate_water_profile(self, params: HydraulicParameters, regime: Dict[str, float]) -> Dict[str, List[float]]:
        """Generate water surface profile along the bridge"""
        
        # Create profile points
        num_points = 21  # 21 points for smooth curve
        total_length = 200  # 200m total length (100m upstream + 100m downstream)
        
        # Chainage points
        chainage = np.linspace(-100, 100, num_points).tolist()
        
        # Water levels
        hfl = params.hfl
        afflux = 0.2  # Assumed afflux for profile generation
        
        water_levels = []
        bed_levels = []
        
        for x in chainage:
            if -50 <= x <= 50:  # Bridge section
                # Gradual rise in water level towards bridge
                rise_factor = 1 - (abs(x) / 50) * 0.3
                water_level = hfl + afflux * rise_factor
            else:
                # Normal water level outside bridge influence
                water_level = hfl
            
            # Bed level (constant slope)
            bed_slope_fraction = self._parse_bed_slope(params.bed_slope)
            bed_level = hfl - regime['regime_depth'] - (x * bed_slope_fraction)
            
            water_levels.append(water_level)
            bed_levels.append(bed_level)
        
        return {
            'chainage': chainage,
            'water_levels': water_levels,
            'bed_levels': bed_levels,
            'bridge_location': [0, 0],  # Bridge at chainage 0
            'hfl_reference': hfl
        }
    
    def _parse_bed_slope(self, bed_slope_str: str) -> float:
        """Parse bed slope string like '1 in 975' to decimal"""
        try:
            if 'in' in bed_slope_str.lower():
                parts = bed_slope_str.lower().split('in')
                if len(parts) == 2:
                    numerator = float(parts[0].strip())
                    denominator = float(parts[1].strip())
                    return numerator / denominator
            return 0.001  # Default slope
        except:
            return 0.001  # Default slope
    
    def _determine_overall_status(self, afflux_results: Dict[str, Any], adequacy_results: Dict[str, Any]) -> str:
        """Determine overall hydraulic design status"""
        
        if adequacy_results['overall_adequacy'] == 'ADEQUATE' and afflux_results['afflux_acceptable']:
            return 'HYDRAULICALLY_SAFE'
        elif afflux_results['afflux_acceptable']:
            return 'AFFLUX_ACCEPTABLE_WATERWAY_REVIEW'
        elif adequacy_results['overall_adequacy'] == 'ADEQUATE':
            return 'WATERWAY_ADEQUATE_AFFLUX_HIGH'
        else:
            return 'REQUIRES_DESIGN_REVISION'
    
    def analyze_from_excel_data(self, excel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze hydraulic data extracted from Excel files"""
        
        # Extract hydraulic parameters from Excel data
        extracted_params = self._extract_params_from_excel(excel_data)
        
        # Run standard analysis
        results = self.analyze(extracted_params)
        
        # Add Excel-specific information
        results['excel_source'] = {
            'filename': excel_data.get('filename', 'unknown'),
            'sheets_processed': list(excel_data.get('sheets', {}).keys()),
            'formulas_used': self._identify_used_formulas(excel_data)
        }
        
        return results
    
    def _extract_params_from_excel(self, excel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract hydraulic parameters from processed Excel data"""
        
        # Default parameters (can be overridden by Excel data)
        params = {
            'discharge': 902.15,  # From Bundan River Bridge example
            'hfl': 101.2,
            'bed_slope': '1 in 975',
            'manning_n': 0.033,
            'silt_factor': 1.5,
            'design_velocity': 3.5,
            'bridge_opening': 75.0,
            'afflux_limit': 0.3
        }
        
        # Try to extract from Excel values
        for sheet_name, sheet_data in excel_data.get('sheets', {}).items():
            values = sheet_data.get('values', {})
            
            # Look for discharge values
            for cell_ref, value in values.items():
                if isinstance(value, (int, float)):
                    # Heuristic matching based on typical ranges
                    if 500 <= value <= 5000:  # Likely discharge
                        params['discharge'] = value
                    elif 95 <= value <= 110:  # Likely HFL
                        params['hfl'] = value
                    elif 0.5 <= value <= 5.0 and value != params['discharge']:  # Likely velocity or silt factor
                        if 2.0 <= value <= 5.0:
                            params['design_velocity'] = value
                        else:
                            params['silt_factor'] = value
        
        return params
    
    def _identify_used_formulas(self, excel_data: Dict[str, Any]) -> Dict[str, str]:
        """Identify hydraulic formulas used in Excel analysis"""
        
        used_formulas = {}
        
        hydraulic_keywords = [
            'discharge', 'velocity', 'afflux', 'scour', 'regime',
            'lacey', 'width', 'depth', 'waterway'
        ]
        
        for sheet_name, sheet_data in excel_data.get('sheets', {}).items():
            formulas = sheet_data.get('formulas', {})
            
            for cell_ref, formula in formulas.items():
                formula_lower = formula.lower()
                if any(keyword in formula_lower for keyword in hydraulic_keywords):
                    used_formulas[f"{sheet_name}!{cell_ref}"] = formula
        
        return used_formulas

