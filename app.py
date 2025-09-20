#!/usr/bin/env python3
"""
Comprehensive Bridge Slab Design Application
Based on PROJECT FILES from Bridge_Slab_Design repository
Integrates all Excel calculation sheets with Claude AI validation
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import io
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Import custom modules
from modules.excel_processor import ExcelProcessor
from modules.bridge_designer import BridgeDesigner
from modules.hydraulic_analyzer import HydraulicAnalyzer
from modules.stability_analyzer import StabilityAnalyzer
from modules.abutment_designer import AbutmentDesigner
from modules.cross_section_designer import CrossSectionDesigner
from modules.claude_integration import ClaudeIntegration
from modules.pdf_generator import PDFGenerator
from modules.master_coordinator import MasterCoordinator
from utils.data_structures import ProjectData, BridgeConfiguration

# Page configuration
st.set_page_config(
    page_title="Bridge Slab Design System",
    page_icon="🌉",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_session_state():
    """Initialize session state variables"""
    if 'project_data' not in st.session_state:
        st.session_state.project_data = None
    if 'excel_files' not in st.session_state:
        st.session_state.excel_files = {}
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = {}
    if 'master_coordinator' not in st.session_state:
        st.session_state.master_coordinator = None

def main():
    initialize_session_state()
    
    st.title("🌉 Comprehensive Bridge Slab Design System")
    st.markdown("### Process Excel calculation sheets and generate detailed engineering reports")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Select Module",
        [
            "Project Setup",
            "Excel File Upload",
            "Stability Analysis",
            "Hydraulic Analysis", 
            "Abutment Design",
            "Cross Section Design",
            "Master Coordination",
            "Claude AI Validation",
            "Generate Reports"
        ]
    )
    
    # Route to appropriate page
    if page == "Project Setup":
        show_project_setup()
    elif page == "Excel File Upload":
        show_excel_upload()
    elif page == "Stability Analysis":
        show_stability_analysis()
    elif page == "Hydraulic Analysis":
        show_hydraulic_analysis()
    elif page == "Abutment Design":
        show_abutment_design()
    elif page == "Cross Section Design":
        show_cross_section_design()
    elif page == "Master Coordination":
        show_master_coordination()
    elif page == "Claude AI Validation":
        show_claude_validation()
    elif page == "Generate Reports":
        show_report_generation()

def show_project_setup():
    """Project setup and configuration page"""
    st.header("Project Setup")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Basic Information")
        bridge_name = st.text_input("Bridge Name", value="Bundan River Bridge")
        location = st.text_input("Location", value="Katumbi Chandrod Road")
        project_type = st.selectbox(
            "Bridge Type",
            ["Submersible Bridge", "High Level Bridge", "Aqueduct", "Culvert"]
        )
        
    with col2:
        st.subheader("Design Parameters")
        span_length = st.number_input("Effective Span (m)", min_value=5.0, max_value=50.0, value=10.0)
        bridge_width = st.number_input("Bridge Width (m)", min_value=3.0, max_value=20.0, value=7.5)
        num_spans = st.number_input("Number of Spans", min_value=1, max_value=10, value=3)
        skew_angle = st.number_input("Skew Angle (degrees)", min_value=0.0, max_value=55.0, value=0.0)
    
    st.subheader("Design Codes and Standards")
    col3, col4 = st.columns(2)
    with col3:
        design_code = st.selectbox("Design Code", ["IRC-6", "IRC-21", "IRC-112", "IS-456"])
        concrete_grade = st.selectbox("Concrete Grade", ["M25", "M30", "M35", "M40"])
    with col4:
        steel_grade = st.selectbox("Steel Grade", ["Fe415", "Fe500", "Fe550"])
        design_life = st.number_input("Design Life (years)", min_value=50, max_value=120, value=100)
    
    if st.button("Create Project Configuration"):
        config = BridgeConfiguration(
            bridge_name=bridge_name,
            location=location,
            project_type=project_type,
            span_length=span_length,
            bridge_width=bridge_width,
            num_spans=num_spans,
            skew_angle=skew_angle,
            design_code=design_code,
            concrete_grade=concrete_grade,
            steel_grade=steel_grade,
            design_life=design_life
        )
        
        st.session_state.project_data = config
        st.session_state.master_coordinator = MasterCoordinator(config)
        
        st.success("✅ Project configuration created successfully!")
        st.json(config.__dict__)

def show_excel_upload():
    """Excel file upload and processing page"""
    st.header("Excel File Upload & Processing")
    
    if st.session_state.project_data is None:
        st.warning("⚠️ Please complete project setup first")
        return
    
    st.subheader("Upload Project Excel Files")
    st.markdown("Upload Excel files from your project directory similar to the Bundan River Bridge TAD structure")
    
    # File upload sections
    upload_sections = {
        "Stability Analysis": "Upload stability analysis Excel files (e.g., '3 Stability Analysis SUBMERSIBLE BRIDGE.xls')",
        "Hydraulic Analysis": "Upload hydraulic calculation Excel files",
        "Live Load Analysis": "Upload live load calculation Excel files (e.g., '02 liveloadtyp for three lanes.xls')",
        "Cross Section": "Upload cross-section design Excel files",
        "Abutment Design": "Upload abutment design Excel files",
        "Foundation Design": "Upload foundation design Excel files",
        "Detailed Estimates": "Upload detailed estimate Excel files"
    }
    
    processor = ExcelProcessor()
    
    for section, description in upload_sections.items():
        with st.expander(f"📁 {section}", expanded=False):
            st.markdown(description)
            
            uploaded_files = st.file_uploader(
                f"Choose {section} files",
                type=['xls', 'xlsx'],
                accept_multiple_files=True,
                key=f"upload_{section.lower().replace(' ', '_')}"
            )
            
            if uploaded_files:
                for file in uploaded_files:
                    if st.button(f"Process {file.name}", key=f"process_{file.name}"):
                        with st.spinner(f"Processing {file.name}..."):
                            try:
                                # Process Excel file and extract formulas
                                processed_data = processor.process_excel_file(file)
                                
                                # Store in session state
                                if section not in st.session_state.excel_files:
                                    st.session_state.excel_files[section] = {}
                                
                                st.session_state.excel_files[section][file.name] = processed_data
                                
                                st.success(f"✅ Successfully processed {file.name}")
                                
                                # Show preview of extracted data
                                st.subheader(f"Preview: {file.name}")
                                
                                # Display sheet summary
                                st.write(f"**Sheets found:** {len(processed_data['sheets'])}")
                                for sheet_name, sheet_data in processed_data['sheets'].items():
                                    st.write(f"- {sheet_name}: {len(sheet_data.get('formulas', {}))} formulas extracted")
                                
                                # Show sample formulas
                                if processed_data['sheets']:
                                    first_sheet = list(processed_data['sheets'].values())[0]
                                    if first_sheet.get('formulas'):
                                        st.write("**Sample Formulas:**")
                                        sample_formulas = dict(list(first_sheet['formulas'].items())[:5])
                                        st.json(sample_formulas)
                                
                            except Exception as e:
                                st.error(f"❌ Error processing {file.name}: {str(e)}")
    
    # Display processed files summary
    if st.session_state.excel_files:
        st.subheader("📊 Processed Files Summary")
        
        total_files = sum(len(files) for files in st.session_state.excel_files.values())
        st.metric("Total Files Processed", total_files)
        
        for section, files in st.session_state.excel_files.items():
            if files:
                st.write(f"**{section}:** {len(files)} files")
                for filename in files.keys():
                    st.write(f"  - {filename}")

def show_stability_analysis():
    """Stability analysis page using processed Excel data"""
    st.header("Stability Analysis")
    
    if not st.session_state.excel_files.get("Stability Analysis"):
        st.warning("⚠️ Please upload stability analysis Excel files first")
        return
    
    analyzer = StabilityAnalyzer(st.session_state.project_data)
    
    # Load stability data from processed Excel files
    stability_files = st.session_state.excel_files["Stability Analysis"]
    
    st.subheader("Available Stability Analysis Files")
    selected_file = st.selectbox(
        "Select file for analysis",
        list(stability_files.keys())
    )
    
    if selected_file and st.button("Run Stability Analysis"):
        with st.spinner("Running stability analysis..."):
            try:
                # Get processed Excel data
                excel_data = stability_files[selected_file]
                
                # Run analysis using original formulas
                results = analyzer.analyze_from_excel_data(excel_data)
                
                # Store results
                st.session_state.analysis_results['stability'] = results
                
                # Display results
                st.success("✅ Stability analysis completed")
                
                # Create tabs for different result views
                tab1, tab2, tab3, tab4 = st.tabs(["Summary", "Detailed Results", "Charts", "Formulas Used"])
                
                with tab1:
                    st.subheader("Stability Analysis Summary")
                    
                    # Key results metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric(
                            "Overturning Factor", 
                            f"{results.get('overturning_factor', 0):.2f}",
                            delta="Safe" if results.get('overturning_factor', 0) > 2.0 else "Check"
                        )
                    
                    with col2:
                        st.metric(
                            "Sliding Factor", 
                            f"{results.get('sliding_factor', 0):.2f}",
                            delta="Safe" if results.get('sliding_factor', 0) > 1.5 else "Check"
                        )
                    
                    with col3:
                        st.metric(
                            "Max Soil Pressure", 
                            f"{results.get('max_soil_pressure', 0):.0f} kN/m²"
                        )
                    
                    with col4:
                        st.metric(
                            "Safety Status",
                            results.get('overall_status', 'Unknown')
                        )
                
                with tab2:
                    st.subheader("Detailed Stability Calculations")
                    
                    # Display calculation steps
                    if 'calculation_steps' in results:
                        for step_name, step_data in results['calculation_steps'].items():
                            st.write(f"**{step_name}**")
                            if isinstance(step_data, dict):
                                st.json(step_data)
                            else:
                                st.write(step_data)
                
                with tab3:
                    st.subheader("Stability Analysis Charts")
                    
                    # Create pressure distribution chart
                    if 'pressure_distribution' in results:
                        fig = go.Figure()
                        
                        pressure_data = results['pressure_distribution']
                        x_coords = pressure_data.get('x_coordinates', [])
                        pressures = pressure_data.get('pressures', [])
                        
                        fig.add_trace(go.Scatter(
                            x=x_coords,
                            y=pressures,
                            mode='lines+markers',
                            name='Soil Pressure',
                            line=dict(color='red', width=3)
                        ))
                        
                        fig.update_layout(
                            title="Soil Pressure Distribution",
                            xaxis_title="Distance from toe (m)",
                            yaxis_title="Pressure (kN/m²)",
                            showlegend=True
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Force diagram
                    if 'forces' in results:
                        forces_data = results['forces']
                        
                        fig2 = go.Figure()
                        
                        # Add force vectors
                        for force_name, force_data in forces_data.items():
                            if isinstance(force_data, dict) and 'magnitude' in force_data:
                                fig2.add_trace(go.Scatter(
                                    x=[0, force_data.get('x_component', 0)],
                                    y=[0, force_data.get('y_component', 0)],
                                    mode='lines+markers',
                                    name=force_name,
                                    line=dict(width=4)
                                ))
                        
                        fig2.update_layout(
                            title="Force Diagram",
                            xaxis_title="Horizontal Force (kN)",
                            yaxis_title="Vertical Force (kN)",
                            showlegend=True
                        )
                        
                        st.plotly_chart(fig2, use_container_width=True)
                
                with tab4:
                    st.subheader("Original Excel Formulas Used")
                    
                    if 'formulas_used' in results:
                        st.write("The following formulas were extracted from the original Excel file:")
                        
                        for formula_ref, formula in results['formulas_used'].items():
                            st.code(f"{formula_ref}: {formula}", language="excel")
                    
                    # Show raw Excel data structure
                    with st.expander("Raw Excel Data Structure"):
                        st.json(excel_data)
                
            except Exception as e:
                st.error(f"❌ Error in stability analysis: {str(e)}")
                st.exception(e)

def show_hydraulic_analysis():
    """Hydraulic analysis page"""
    st.header("Hydraulic Analysis")
    
    if not st.session_state.excel_files.get("Hydraulic Analysis"):
        st.warning("⚠️ Please upload hydraulic analysis Excel files first")
        return
    
    analyzer = HydraulicAnalyzer(st.session_state.project_data)
    
    # Input parameters
    st.subheader("Hydraulic Design Parameters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        discharge = st.number_input("Design Discharge (cumecs)", min_value=100.0, max_value=5000.0, value=902.15)
        hfl = st.number_input("High Flood Level (m)", min_value=90.0, max_value=120.0, value=101.2)
        bed_slope = st.text_input("Bed Slope", value="1 in 975")
        manning_n = st.number_input("Manning's n", min_value=0.02, max_value=0.05, value=0.033)
    
    with col2:
        silt_factor = st.number_input("Lacey's Silt Factor", min_value=0.5, max_value=3.0, value=1.5)
        design_velocity = st.number_input("Design Velocity (m/s)", min_value=2.0, max_value=5.0, value=3.5)
        afflux_limit = st.number_input("Allowable Afflux (m)", min_value=0.1, max_value=1.0, value=0.3)
        bridge_opening = st.number_input("Bridge Opening (m)", min_value=20.0, max_value=200.0, value=75.0)
    
    if st.button("Run Hydraulic Analysis"):
        with st.spinner("Running hydraulic analysis..."):
            try:
                # Prepare hydraulic data
                hydraulic_data = {
                    'discharge': discharge,
                    'hfl': hfl,
                    'bed_slope': bed_slope,
                    'manning_n': manning_n,
                    'silt_factor': silt_factor,
                    'design_velocity': design_velocity,
                    'afflux_limit': afflux_limit,
                    'bridge_opening': bridge_opening
                }
                
                # Run analysis
                results = analyzer.analyze(hydraulic_data)
                
                # Store results
                st.session_state.analysis_results['hydraulic'] = results
                
                # Display results
                st.success("✅ Hydraulic analysis completed")
                
                # Results tabs
                tab1, tab2, tab3 = st.tabs(["Summary", "Detailed Calculations", "Charts"])
                
                with tab1:
                    st.subheader("Hydraulic Analysis Summary")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Regime Width", f"{results.get('regime_width', 0):.1f} m")
                        st.metric("Effective Waterway", f"{results.get('effective_waterway', 0):.1f} m")
                    
                    with col2:
                        st.metric("Calculated Afflux", f"{results.get('afflux', 0):.3f} m")
                        st.metric("Scour Depth", f"{results.get('scour_depth', 0):.1f} m")
                    
                    with col3:
                        st.metric("Pier Spacing", f"{results.get('pier_spacing', 0):.1f} m")
                        st.metric("Hydraulic Status", results.get('status', 'Unknown'))
                
                with tab2:
                    st.subheader("Detailed Hydraulic Calculations")
                    
                    # Lacey's Regime Theory
                    st.write("**Lacey's Regime Theory Results:**")
                    st.write(f"- Regime Width (Wr) = {results.get('regime_width', 0):.2f} m")
                    st.write(f"- Regime Depth (Dr) = {results.get('regime_depth', 0):.2f} m")
                    st.write(f"- Regime Velocity (Vr) = {results.get('regime_velocity', 0):.2f} m/s")
                    
                    # Afflux Calculation
                    st.write("**Afflux Calculation:**")
                    st.write(f"- Approach Velocity = {results.get('approach_velocity', 0):.2f} m/s")
                    st.write(f"- Bridge Velocity = {results.get('bridge_velocity', 0):.2f} m/s")
                    st.write(f"- Calculated Afflux = {results.get('afflux', 0):.3f} m")
                    
                    # Scour Analysis
                    st.write("**Scour Analysis:**")
                    st.write(f"- Design Scour Depth = {results.get('scour_depth', 0):.2f} m")
                    st.write(f"- Foundation Level Required = {results.get('foundation_level', 0):.2f} m")
                
                with tab3:
                    st.subheader("Hydraulic Analysis Charts")
                    
                    # Water surface profile
                    if 'water_profile' in results:
                        fig1 = go.Figure()
                        
                        profile_data = results['water_profile']
                        x_coords = profile_data.get('chainage', [])
                        water_levels = profile_data.get('water_levels', [])
                        bed_levels = profile_data.get('bed_levels', [])
                        
                        fig1.add_trace(go.Scatter(
                            x=x_coords, y=water_levels,
                            mode='lines', name='Water Surface',
                            line=dict(color='blue', width=3)
                        ))
                        
                        fig1.add_trace(go.Scatter(
                            x=x_coords, y=bed_levels,
                            mode='lines', name='Bed Level',
                            line=dict(color='brown', width=2),
                            fill='tonexty'
                        ))
                        
                        fig1.update_layout(
                            title="Water Surface Profile",
                            xaxis_title="Chainage (m)",
                            yaxis_title="Level (m)",
                            showlegend=True
                        )
                        
                        st.plotly_chart(fig1, use_container_width=True)
                    
                    # Velocity distribution
                    if 'velocity_distribution' in results:
                        fig2 = go.Figure()
                        
                        vel_data = results['velocity_distribution']
                        sections = vel_data.get('sections', [])
                        velocities = vel_data.get('velocities', [])
                        
                        fig2.add_trace(go.Bar(
                            x=sections, y=velocities,
                            name='Velocity Distribution',
                            marker_color='lightblue'
                        ))
                        
                        fig2.update_layout(
                            title="Velocity Distribution Across Bridge",
                            xaxis_title="Section",
                            yaxis_title="Velocity (m/s)",
                            showlegend=True
                        )
                        
                        st.plotly_chart(fig2, use_container_width=True)
                
            except Exception as e:
                st.error(f"❌ Error in hydraulic analysis: {str(e)}")
                st.exception(e)

def show_abutment_design():
    """Abutment design page"""
    st.header("Abutment Design")
    
    if not st.session_state.project_data:
        st.warning("⚠️ Please complete project setup first")
        return
    
    designer = AbutmentDesigner(st.session_state.project_data)
    
    st.subheader("Abutment Type Selection")
    abutment_type = st.selectbox(
        "Select Abutment Type",
        ["Type-1 Battered Faces", "Type-2 Cantilever", "Type-3 Counterfort"]
    )
    
    # Abutment parameters
    st.subheader("Design Parameters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        height = st.number_input("Abutment Height (m)", min_value=3.0, max_value=15.0, value=6.5)
        stem_top = st.number_input("Stem Thickness at Top (m)", min_value=0.3, max_value=1.0, value=0.5)
        stem_base = st.number_input("Stem Thickness at Base (m)", min_value=0.5, max_value=2.0, value=1.2)
        
    with col2:
        base_length = st.number_input("Base Length (m)", min_value=3.0, max_value=12.0, value=7.0)
        base_width = st.number_input("Base Width (m)", min_value=2.0, max_value=8.0, value=3.5)
        heel_length = st.number_input("Heel Length (m)", min_value=1.0, max_value=6.0, value=4.0)
    
    # Soil parameters
    st.subheader("Soil Properties")
    col3, col4 = st.columns(2)
    
    with col3:
        sbc = st.number_input("Safe Bearing Capacity (kN/m²)", min_value=100.0, max_value=1000.0, value=450.0)
        angle_friction = st.number_input("Angle of Internal Friction (°)", min_value=20.0, max_value=45.0, value=30.0)
        
    with col4:
        unit_weight = st.number_input("Unit Weight of Soil (kN/m³)", min_value=16.0, max_value=22.0, value=18.0)
        cohesion = st.number_input("Cohesion (kN/m²)", min_value=0.0, max_value=50.0, value=15.0)
    
    if st.button("Design Abutment"):
        with st.spinner("Designing abutment..."):
            try:
                # Prepare design parameters
                design_params = {
                    'type': abutment_type,
                    'height': height,
                    'stem_top': stem_top,
                    'stem_base': stem_base,
                    'base_length': base_length,
                    'base_width': base_width,
                    'heel_length': heel_length,
                    'sbc': sbc,
                    'angle_friction': angle_friction,
                    'unit_weight': unit_weight,
                    'cohesion': cohesion
                }
                
                # Run design
                results = designer.design(design_params)
                
                # Store results
                st.session_state.analysis_results['abutment'] = results
                
                # Display results
                st.success("✅ Abutment design completed")
                
                # Results display
                tab1, tab2, tab3, tab4 = st.tabs(["Design Summary", "Stability Check", "Reinforcement", "Drawings"])
                
                with tab1:
                    st.subheader("Abutment Design Summary")
                    
                    # Design status
                    if results.get('design_status') == 'SAFE':
                        st.success("✅ Design is SAFE")
                    else:
                        st.error("❌ Design needs revision")
                    
                    # Key dimensions
                    st.write("**Final Dimensions:**")
                    st.write(f"- Abutment Height: {results.get('final_height', height):.2f} m")
                    st.write(f"- Base Dimensions: {results.get('final_base_length', base_length):.2f} × {results.get('final_base_width', base_width):.2f} m")
                    st.write(f"- Stem Thickness: {results.get('final_stem_top', stem_top):.2f} - {results.get('final_stem_base', stem_base):.2f} m")
                    
                    # Material quantities
                    st.write("**Material Quantities:**")
                    st.write(f"- Concrete Volume: {results.get('concrete_volume', 0):.2f} m³")
                    st.write(f"- Steel Weight: {results.get('steel_weight', 0):.0f} kg")
                
                with tab2:
                    st.subheader("Stability Check Results")
                    
                    # Safety factors
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric(
                            "Overturning Factor",
                            f"{results.get('overturning_factor', 0):.2f}",
                            delta="Safe" if results.get('overturning_factor', 0) > 2.0 else "Check"
                        )
                    
                    with col2:
                        st.metric(
                            "Sliding Factor",
                            f"{results.get('sliding_factor', 0):.2f}",
                            delta="Safe" if results.get('sliding_factor', 0) > 1.5 else "Check"
                        )
                    
                    with col3:
                        st.metric(
                            "Max Pressure",
                            f"{results.get('max_pressure', 0):.0f} kN/m²"
                        )
                    
                    # Detailed stability calculations
                    if 'stability_details' in results:
                        st.write("**Detailed Calculations:**")
                        stability = results['stability_details']
                        
                        st.write(f"- Total Vertical Load: {stability.get('total_vertical', 0):.1f} kN")
                        st.write(f"- Total Horizontal Load: {stability.get('total_horizontal', 0):.1f} kN")
                        st.write(f"- Overturning Moment: {stability.get('overturning_moment', 0):.1f} kN-m")
                        st.write(f"- Resisting Moment: {stability.get('resisting_moment', 0):.1f} kN-m")
                
                with tab3:
                    st.subheader("Reinforcement Design")
                    
                    if 'reinforcement' in results:
                        rebar = results['reinforcement']
                        
                        st.write("**Stem Reinforcement:**")
                        st.write(f"- Main Bars: {rebar.get('stem_main_bars', 'Not calculated')}")
                        st.write(f"- Distribution Bars: {rebar.get('stem_dist_bars', 'Not calculated')}")
                        st.write(f"- Shear Reinforcement: {rebar.get('stem_shear_bars', 'Not calculated')}")
                        
                        st.write("**Base Reinforcement:**")
                        st.write(f"- Longitudinal Bars: {rebar.get('base_long_bars', 'Not calculated')}")
                        st.write(f"- Transverse Bars: {rebar.get('base_trans_bars', 'Not calculated')}")
                        
                        # Reinforcement drawing placeholder
                        st.write("**Reinforcement Layout:**")
                        
                        # Create a simple reinforcement layout diagram
                        fig = go.Figure()
                        
                        # Draw abutment outline
                        fig.add_shape(
                            type="rect",
                            x0=0, y0=0, x1=base_length, y1=0.5,
                            line=dict(color="black", width=2),
                            fillcolor="lightgray"
                        )
                        
                        # Draw stem
                        fig.add_shape(
                            type="path",
                            path=f"M {heel_length} 0.5 L {heel_length} {height + 0.5} L {heel_length + stem_top} {height + 0.5} L {heel_length + stem_base} 0.5 Z",
                            line=dict(color="black", width=2),
                            fillcolor="lightgray"
                        )
                        
                        fig.update_layout(
                            title="Abutment Cross-Section",
                            xaxis_title="Length (m)",
                            yaxis_title="Height (m)",
                            showlegend=False,
                            yaxis=dict(scaleanchor="x", scaleratio=1)
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                
                with tab4:
                    st.subheader("Design Drawings")
                    
                    st.write("**Abutment General Arrangement:**")
                    
                    # Create detailed technical drawing
                    fig = make_subplots(
                        rows=2, cols=2,
                        subplot_titles=("Elevation View", "Plan View", "Section A-A", "Reinforcement Details"),
                        specs=[[{"type": "scatter"}, {"type": "scatter"}],
                               [{"type": "scatter"}, {"type": "scatter"}]]
                    )
                    
                    # Elevation view
                    fig.add_trace(
                        go.Scatter(
                            x=[0, base_length, heel_length + stem_base, heel_length + stem_top, heel_length, 0, 0],
                            y=[0, 0, 0.5, height + 0.5, height + 0.5, 0.5, 0],
                            mode='lines',
                            fill='toself',
                            name='Abutment Elevation',
                            fillcolor='lightblue',
                            line=dict(color='black', width=2)
                        ),
                        row=1, col=1
                    )
                    
                    # Plan view
                    fig.add_trace(
                        go.Scatter(
                            x=[0, base_length, base_length, 0, 0],
                            y=[0, 0, base_width, base_width, 0],
                            mode='lines',
                            fill='toself',
                            name='Abutment Plan',
                            fillcolor='lightgreen',
                            line=dict(color='black', width=2)
                        ),
                        row=1, col=2
                    )
                    
                    fig.update_layout(
                        title="Abutment Design Drawings",
                        showlegend=False,
                        height=800
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"❌ Error in abutment design: {str(e)}")
                st.exception(e)

def show_cross_section_design():
    """Cross section design page"""
    st.header("Cross Section Design")
    
    if not st.session_state.project_data:
        st.warning("⚠️ Please complete project setup first")
        return
    
    designer = CrossSectionDesigner(st.session_state.project_data)
    
    st.subheader("Bridge Cross Section Parameters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        carriageway_width = st.number_input("Carriageway Width (m)", min_value=5.0, max_value=15.0, value=7.5)
        footpath_width = st.number_input("Footpath Width (each side) (m)", min_value=0.0, max_value=2.0, value=1.0)
        crash_barrier_width = st.number_input("Crash Barrier Width (each side) (m)", min_value=0.0, max_value=1.0, value=0.5)
        
    with col2:
        slab_thickness = st.number_input("Slab Thickness (m)", min_value=0.2, max_value=1.0, value=0.5)
        wearing_coat = st.number_input("Wearing Coat Thickness (m)", min_value=0.05, max_value=0.15, value=0.075)
        edge_beam_width = st.number_input("Edge Beam Width (m)", min_value=0.3, max_value=0.8, value=0.5)
    
    # Load parameters
    st.subheader("Load Parameters")
    col3, col4 = st.columns(2)
    
    with col3:
        live_load_class = st.selectbox("Live Load Class", ["Class A", "Class AA", "Class 70R", "Class A + 70R"])
        impact_factor = st.number_input("Impact Factor", min_value=0.0, max_value=0.5, value=0.25)
        
    with col4:
        load_factor_dl = st.number_input("Load Factor (Dead Load)", min_value=1.0, max_value=2.0, value=1.35)
        load_factor_ll = st.number_input("Load Factor (Live Load)", min_value=1.0, max_value=2.5, value=1.75)
    
    if st.button("Design Cross Section"):
        with st.spinner("Designing cross section..."):
            try:
                # Prepare design parameters
                design_params = {
                    'carriageway_width': carriageway_width,
                    'footpath_width': footpath_width,
                    'crash_barrier_width': crash_barrier_width,
                    'slab_thickness': slab_thickness,
                    'wearing_coat': wearing_coat,
                    'edge_beam_width': edge_beam_width,
                    'live_load_class': live_load_class,
                    'impact_factor': impact_factor,
                    'load_factor_dl': load_factor_dl,
                    'load_factor_ll': load_factor_ll
                }
                
                # Run design
                results = designer.design(design_params)
                
                # Store results
                st.session_state.analysis_results['cross_section'] = results
                
                # Display results
                st.success("✅ Cross section design completed")
                
                # Results tabs
                tab1, tab2, tab3, tab4 = st.tabs(["Design Summary", "Load Analysis", "Reinforcement", "Cross Section"])
                
                with tab1:
                    st.subheader("Cross Section Design Summary")
                    
                    # Design status
                    if results.get('design_status') == 'SAFE':
                        st.success("✅ Design is SAFE")
                    else:
                        st.error("❌ Design needs revision")
                    
                    # Key results
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Width", f"{results.get('total_width', 0):.2f} m")
                        st.metric("Effective Depth", f"{results.get('effective_depth', 0):.3f} m")
                    
                    with col2:
                        st.metric("Max Moment", f"{results.get('max_moment', 0):.1f} kN-m/m")
                        st.metric("Max Shear", f"{results.get('max_shear', 0):.1f} kN/m")
                    
                    with col3:
                        st.metric("Required Steel", f"{results.get('steel_required', 0):.0f} mm²/m")
                        st.metric("Deflection", f"{results.get('deflection', 0):.1f} mm")
                
                with tab2:
                    st.subheader("Load Analysis Results")
                    
                    if 'load_analysis' in results:
                        loads = results['load_analysis']
                        
                        st.write("**Dead Loads:**")
                        st.write(f"- Self Weight: {loads.get('self_weight', 0):.1f} kN/m²")
                        st.write(f"- Wearing Coat: {loads.get('wearing_coat', 0):.1f} kN/m²")
                        st.write(f"- Crash Barrier: {loads.get('crash_barrier', 0):.1f} kN/m")
                        st.write(f"- Total Dead Load: {loads.get('total_dead_load', 0):.1f} kN/m²")
                        
                        st.write("**Live Loads:**")
                        st.write(f"- Live Load Intensity: {loads.get('live_load_intensity', 0):.1f} kN/m²")
                        st.write(f"- Impact Factor: {loads.get('impact_factor', impact_factor):.2f}")
                        st.write(f"- Total Live Load: {loads.get('total_live_load', 0):.1f} kN/m²")
                        
                        st.write("**Design Loads:**")
                        st.write(f"- Factored Dead Load: {loads.get('factored_dl', 0):.1f} kN/m²")
                        st.write(f"- Factored Live Load: {loads.get('factored_ll', 0):.1f} kN/m²")
                        st.write(f"- Total Design Load: {loads.get('total_design_load', 0):.1f} kN/m²")
                    
                    # Load distribution chart
                    if 'load_distribution' in results:
                        dist_data = results['load_distribution']
                        
                        fig = go.Figure()
                        
                        x_coords = dist_data.get('x_coordinates', [])
                        dead_loads = dist_data.get('dead_loads', [])
                        live_loads = dist_data.get('live_loads', [])
                        
                        fig.add_trace(go.Scatter(
                            x=x_coords, y=dead_loads,
                            mode='lines', name='Dead Load',
                            line=dict(color='red', width=3)
                        ))
                        
                        fig.add_trace(go.Scatter(
                            x=x_coords, y=live_loads,
                            mode='lines', name='Live Load',
                            line=dict(color='blue', width=3)
                        ))
                        
                        fig.update_layout(
                            title="Load Distribution Across Width",
                            xaxis_title="Distance (m)",
                            yaxis_title="Load (kN/m²)",
                            showlegend=True
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                
                with tab3:
                    st.subheader("Reinforcement Design")
                    
                    if 'reinforcement' in results:
                        rebar = results['reinforcement']
                        
                        st.write("**Main Reinforcement (Bottom):**")
                        st.write(f"- Required Area: {rebar.get('main_steel_required', 0):.0f} mm²/m")
                        st.write(f"- Provided: {rebar.get('main_steel_provided', 'Not calculated')}")
                        
                        st.write("**Distribution Reinforcement (Top):**")
                        st.write(f"- Required Area: {rebar.get('dist_steel_required', 0):.0f} mm²/m")
                        st.write(f"- Provided: {rebar.get('dist_steel_provided', 'Not calculated')}")
                        
                        st.write("**Shear Reinforcement:**")
                        st.write(f"- Shear Check: {rebar.get('shear_check', 'Not calculated')}")
                        st.write(f"- Stirrups Required: {rebar.get('stirrups_required', 'Not calculated')}")
                        
                        # Reinforcement layout chart
                        if 'rebar_layout' in rebar:
                            layout_data = rebar['rebar_layout']
                            
                            fig = go.Figure()
                            
                            # Draw slab outline
                            fig.add_shape(
                                type="rect",
                                x0=0, y0=0, x1=results.get('total_width', 10), y1=slab_thickness,
                                line=dict(color="black", width=2),
                                fillcolor="lightgray"
                            )
                            
                            # Add reinforcement bars (simplified representation)
                            total_width = results.get('total_width', 10)
                            bar_spacing = 0.15  # 150mm spacing
                            
                            # Bottom bars
                            for x in np.arange(0.05, total_width, bar_spacing):
                                fig.add_shape(
                                    type="circle",
                                    x0=x-0.01, y0=0.05-0.01, x1=x+0.01, y1=0.05+0.01,
                                    fillcolor="red", line=dict(color="red")
                                )
                            
                            # Top bars
                            for x in np.arange(0.075, total_width, bar_spacing*2):
                                fig.add_shape(
                                    type="circle",
                                    x0=x-0.01, y0=slab_thickness-0.05-0.01, x1=x+0.01, y1=slab_thickness-0.05+0.01,
                                    fillcolor="blue", line=dict(color="blue")
                                )
                            
                            fig.update_layout(
                                title="Reinforcement Layout (Cross Section)",
                                xaxis_title="Width (m)",
                                yaxis_title="Thickness (m)",
                                showlegend=False,
                                yaxis=dict(scaleanchor="x", scaleratio=1)
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                
                with tab4:
                    st.subheader("Bridge Cross Section")
                    
                    # Detailed cross section drawing
                    fig = go.Figure()
                    
                    total_width = results.get('total_width', carriageway_width + 2*footpath_width + 2*crash_barrier_width)
                    
                    # Draw main slab
                    fig.add_shape(
                        type="rect",
                        x0=0, y0=0, x1=total_width, y1=slab_thickness,
                        line=dict(color="black", width=2),
                        fillcolor="lightblue",
                        name="Main Slab"
                    )
                    
                    # Draw wearing coat
                    fig.add_shape(
                        type="rect",
                        x0=crash_barrier_width, y0=slab_thickness, 
                        x1=total_width-crash_barrier_width, y1=slab_thickness+wearing_coat,
                        line=dict(color="black", width=1),
                        fillcolor="gray",
                        name="Wearing Coat"
                    )
                    
                    # Draw footpaths
                    if footpath_width > 0:
                        # Left footpath
                        fig.add_shape(
                            type="rect",
                            x0=crash_barrier_width, y0=slab_thickness+wearing_coat,
                            x1=crash_barrier_width+footpath_width, y1=slab_thickness+wearing_coat+0.15,
                            line=dict(color="black", width=1),
                            fillcolor="lightgreen"
                        )
                        
                        # Right footpath
                        fig.add_shape(
                            type="rect",
                            x0=total_width-crash_barrier_width-footpath_width, y0=slab_thickness+wearing_coat,
                            x1=total_width-crash_barrier_width, y1=slab_thickness+wearing_coat+0.15,
                            line=dict(color="black", width=1),
                            fillcolor="lightgreen"
                        )
                    
                    # Draw crash barriers
                    if crash_barrier_width > 0:
                        # Left barrier
                        fig.add_shape(
                            type="rect",
                            x0=0, y0=slab_thickness, x1=crash_barrier_width, y1=slab_thickness+1.0,
                            line=dict(color="black", width=2),
                            fillcolor="orange"
                        )
                        
                        # Right barrier
                        fig.add_shape(
                            type="rect",
                            x0=total_width-crash_barrier_width, y0=slab_thickness,
                            x1=total_width, y1=slab_thickness+1.0,
                            line=dict(color="black", width=2),
                            fillcolor="orange"
                        )
                    
                    # Add dimensions
                    fig.add_annotation(
                        x=total_width/2, y=-0.3,
                        text=f"Total Width: {total_width:.2f} m",
                        showarrow=False,
                        font=dict(size=12, color="black")
                    )
                    
                    fig.add_annotation(
                        x=total_width + 0.5, y=slab_thickness/2,
                        text=f"Slab: {slab_thickness:.2f} m",
                        showarrow=False,
                        font=dict(size=10, color="black"),
                        textangle=90
                    )
                    
                    fig.update_layout(
                        title="Bridge Cross Section",
                        xaxis_title="Width (m)",
                        yaxis_title="Height (m)",
                        showlegend=False,
                        yaxis=dict(scaleanchor="x", scaleratio=1),
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Cross section details table
                    st.write("**Cross Section Components:**")
                    components_data = [
                        ["Component", "Width (m)", "Thickness (m)", "Area (m²)"],
                        ["Carriageway", f"{carriageway_width:.2f}", f"{wearing_coat:.3f}", f"{carriageway_width * wearing_coat:.3f}"],
                        ["Footpath (each)", f"{footpath_width:.2f}", "0.150", f"{footpath_width * 0.15:.3f}"],
                        ["Crash Barrier (each)", f"{crash_barrier_width:.2f}", "1.000", f"{crash_barrier_width * 1.0:.3f}"],
                        ["Main Slab", f"{total_width:.2f}", f"{slab_thickness:.3f}", f"{total_width * slab_thickness:.3f}"],
                        ["Total Width", f"{total_width:.2f}", "-", "-"]
                    ]
                    
                    df_components = pd.DataFrame(components_data[1:], columns=components_data[0])
                    st.dataframe(df_components, use_container_width=True)
                
            except Exception as e:
                st.error(f"❌ Error in cross section design: {str(e)}")
                st.exception(e)

def show_master_coordination():
    """Master coordination page"""
    st.header("Master Excel Coordination System")
    
    if not st.session_state.master_coordinator:
        st.warning("⚠️ Please complete project setup first")
        return
    
    coordinator = st.session_state.master_coordinator
    
    st.subheader("Design Integration Status")
    
    # Check what analyses have been completed
    analyses_status = {}
    for analysis in ['stability', 'hydraulic', 'abutment', 'cross_section']:
        analyses_status[analysis] = analysis in st.session_state.analysis_results
    
    # Display status
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_icon = "✅" if analyses_status['stability'] else "⏳"
        st.metric("Stability Analysis", status_icon)
    
    with col2:
        status_icon = "✅" if analyses_status['hydraulic'] else "⏳"
        st.metric("Hydraulic Analysis", status_icon)
    
    with col3:
        status_icon = "✅" if analyses_status['abutment'] else "⏳"
        st.metric("Abutment Design", status_icon)
    
    with col4:
        status_icon = "✅" if analyses_status['cross_section'] else "⏳"
        st.metric("Cross Section", status_icon)
    
    # Integration options
    st.subheader("Integration Actions")
    
    if st.button("Create Master Excel File"):
        with st.spinner("Creating master Excel file..."):
            try:
                # Coordinate all analyses
                master_data = coordinator.create_master_file(st.session_state.analysis_results)
                
                # Generate Excel file
                excel_buffer = coordinator.generate_master_excel(master_data)
                
                st.success("✅ Master Excel file created successfully!")
                
                # Download button
                st.download_button(
                    label="📥 Download Master Excel File",
                    data=excel_buffer.getvalue(),
                    file_name=f"Master_Bridge_Design_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
                # Display summary
                st.subheader("Master File Summary")
                
                if 'summary' in master_data:
                    summary = master_data['summary']
                    
                    st.write(f"**Total Sheets Created:** {summary.get('total_sheets', 0)}")
                    st.write(f"**Total Formulas Linked:** {summary.get('total_formulas', 0)}")
                    st.write(f"**Integration Status:** {summary.get('integration_status', 'Unknown')}")
                    
                    # Show sheet list
                    if 'sheet_list' in summary:
                        st.write("**Sheets in Master File:**")
                        for i, sheet_name in enumerate(summary['sheet_list'], 1):
                            st.write(f"{i}. {sheet_name}")
                
            except Exception as e:
                st.error(f"❌ Error creating master file: {str(e)}")
                st.exception(e)
    
    # Formula linking status
    st.subheader("Formula Linking Analysis")
    
    if st.session_state.analysis_results:
        st.write("**Cross-Referenced Parameters:**")
        
        # Identify common parameters across analyses
        common_params = coordinator.identify_common_parameters(st.session_state.analysis_results)
        
        if common_params:
            for param_group, params in common_params.items():
                st.write(f"**{param_group}:**")
                for param in params:
                    st.write(f"  - {param}")
        else:
            st.write("No common parameters identified for linking.")
    
    # Consistency check
    if all(analyses_status.values()):
        st.subheader("Design Consistency Check")
        
        if st.button("Run Consistency Check"):
            with st.spinner("Checking design consistency..."):
                try:
                    consistency_results = coordinator.check_consistency(st.session_state.analysis_results)
                    
                    if consistency_results.get('overall_status') == 'CONSISTENT':
                        st.success("✅ All designs are consistent")
                    else:
                        st.warning("⚠️ Some inconsistencies found")
                    
                    # Display detailed results
                    if 'checks' in consistency_results:
                        for check_name, check_result in consistency_results['checks'].items():
                            if check_result.get('status') == 'PASS':
                                st.success(f"✅ {check_name}: {check_result.get('message', 'OK')}")
                            else:
                                st.error(f"❌ {check_name}: {check_result.get('message', 'Failed')}")
                    
                except Exception as e:
                    st.error(f"❌ Error in consistency check: {str(e)}")

def show_claude_validation():
    """Claude AI validation page"""
    st.header("Claude AI Formula Validation & Optimization")
    
    if not st.session_state.analysis_results:
        st.warning("⚠️ Please complete some analyses first")
        return
    
    # Check for Claude API key
    claude_api_key = os.getenv('ANTHROPIC_API_KEY')
    if not claude_api_key:
        st.error("❌ ANTHROPIC_API_KEY not found in environment variables")
        return
    
    claude = ClaudeIntegration()
    
    st.subheader("AI-Powered Design Validation")
    
    # Select analysis for validation
    available_analyses = list(st.session_state.analysis_results.keys())
    selected_analysis = st.selectbox("Select Analysis for Validation", available_analyses)
    
    # Validation options
    validation_type = st.selectbox(
        "Validation Type",
        [
            "Formula Verification",
            "Design Optimization", 
            "Code Compliance Check",
            "Safety Factor Review",
            "Alternative Design Suggestions"
        ]
    )
    
    # Custom prompt option
    custom_prompt = st.text_area(
        "Custom Instructions (optional)",
        placeholder="Add specific questions or requirements for Claude to analyze..."
    )
    
    if st.button("Validate with Claude AI"):
        with st.spinner("Consulting Claude AI for validation..."):
            try:
                analysis_data = st.session_state.analysis_results[selected_analysis]
                
                # Prepare context for Claude
                validation_context = {
                    'analysis_type': selected_analysis,
                    'validation_type': validation_type,
                    'analysis_data': analysis_data,
                    'project_data': st.session_state.project_data.__dict__ if st.session_state.project_data else {},
                    'custom_instructions': custom_prompt
                }
                
                # Get Claude's analysis
                claude_response = claude.validate_design(validation_context)
                
                st.success("✅ Claude AI validation completed")
                
                # Display results in tabs
                tab1, tab2, tab3, tab4 = st.tabs(["AI Summary", "Detailed Analysis", "Recommendations", "Formula Check"])
                
                with tab1:
                    st.subheader("Claude AI Summary")
                    
                    if 'summary' in claude_response:
                        st.write(claude_response['summary'])
                    
                    # Key findings
                    if 'key_findings' in claude_response:
                        st.write("**Key Findings:**")
                        for finding in claude_response['key_findings']:
                            st.write(f"- {finding}")
                    
                    # Overall assessment
                    if 'overall_assessment' in claude_response:
                        assessment = claude_response['overall_assessment']
                        if assessment.get('status') == 'ACCEPTABLE':
                            st.success(f"✅ {assessment.get('message', 'Design is acceptable')}")
                        elif assessment.get('status') == 'NEEDS_REVIEW':
                            st.warning(f"⚠️ {assessment.get('message', 'Design needs review')}")
                        else:
                            st.error(f"❌ {assessment.get('message', 'Design has issues')}")
                
                with tab2:
                    st.subheader("Detailed AI Analysis")
                    
                    if 'detailed_analysis' in claude_response:
                        for section, content in claude_response['detailed_analysis'].items():
                            st.write(f"**{section}:**")
                            st.write(content)
                            st.write("---")
                    
                    # Technical commentary
                    if 'technical_commentary' in claude_response:
                        st.write("**Technical Commentary:**")
                        st.write(claude_response['technical_commentary'])
                
                with tab3:
                    st.subheader("AI Recommendations")
                    
                    if 'recommendations' in claude_response:
                        recommendations = claude_response['recommendations']
                        
                        # Priority recommendations
                        if 'high_priority' in recommendations:
                            st.write("**High Priority Recommendations:**")
                            for rec in recommendations['high_priority']:
                                st.error(f"🔴 {rec}")
                        
                        # Medium priority
                        if 'medium_priority' in recommendations:
                            st.write("**Medium Priority Recommendations:**")
                            for rec in recommendations['medium_priority']:
                                st.warning(f"🟡 {rec}")
                        
                        # Low priority
                        if 'low_priority' in recommendations:
                            st.write("**Low Priority Recommendations:**")
                            for rec in recommendations['low_priority']:
                                st.info(f"🔵 {rec}")
                    
                    # Optimization suggestions
                    if 'optimization_suggestions' in claude_response:
                        st.write("**Optimization Suggestions:**")
                        for suggestion in claude_response['optimization_suggestions']:
                            st.write(f"💡 {suggestion}")
                
                with tab4:
                    st.subheader("Formula Verification")
                    
                    if 'formula_check' in claude_response:
                        formula_results = claude_response['formula_check']
                        
                        # Verified formulas
                        if 'verified_formulas' in formula_results:
                            st.write("**Verified Formulas:**")
                            for formula in formula_results['verified_formulas']:
                                st.success(f"✅ {formula}")
                        
                        # Questionable formulas
                        if 'questionable_formulas' in formula_results:
                            st.write("**Formulas Needing Review:**")
                            for formula in formula_results['questionable_formulas']:
                                st.warning(f"⚠️ {formula}")
                        
                        # Incorrect formulas
                        if 'incorrect_formulas' in formula_results:
                            st.write("**Potentially Incorrect Formulas:**")
                            for formula in formula_results['incorrect_formulas']:
                                st.error(f"❌ {formula}")
                    
                    # Alternative formulations
                    if 'alternative_formulations' in claude_response:
                        st.write("**Alternative Formula Suggestions:**")
                        for alt in claude_response['alternative_formulations']:
                            st.code(alt, language="text")
                
                # Store Claude results
                if 'claude_validations' not in st.session_state:
                    st.session_state.claude_validations = {}
                
                st.session_state.claude_validations[f"{selected_analysis}_{validation_type}"] = claude_response
                
            except Exception as e:
                st.error(f"❌ Error in Claude validation: {str(e)}")
                st.exception(e)
    
    # Show previous validations
    if hasattr(st.session_state, 'claude_validations') and st.session_state.claude_validations:
        st.subheader("Previous AI Validations")
        
        for validation_key, validation_data in st.session_state.claude_validations.items():
            with st.expander(f"📋 {validation_key}"):
                if 'summary' in validation_data:
                    st.write(validation_data['summary'])
                if 'overall_assessment' in validation_data:
                    st.json(validation_data['overall_assessment'])

def show_report_generation():
    """Comprehensive report generation page"""
    st.header("Generate Comprehensive Design Reports")
    
    if not st.session_state.analysis_results:
        st.warning("⚠️ Please complete some analyses first")
        return
    
    st.subheader("Report Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        report_type = st.selectbox(
            "Report Type",
            ["Complete Design Report (250+ pages)", "Executive Summary", "Technical Calculations Only", "Custom Report"]
        )
        
        include_sections = st.multiselect(
            "Include Sections",
            ["Project Overview", "Stability Analysis", "Hydraulic Analysis", "Abutment Design", 
             "Cross Section Design", "Reinforcement Details", "Construction Drawings", 
             "Bill of Quantities", "Claude AI Validation", "Appendices"],
            default=["Project Overview", "Stability Analysis", "Hydraulic Analysis", "Abutment Design", "Cross Section Design"]
        )
    
    with col2:
        output_format = st.selectbox("Output Format", ["PDF", "HTML", "Word Document"])
        include_calculations = st.checkbox("Include Detailed Calculations", value=True)
        include_drawings = st.checkbox("Include Technical Drawings", value=True)
        include_photos = st.checkbox("Include Reference Photos", value=False)
    
    # Report customization
    st.subheader("Report Customization")
    
    company_name = st.text_input("Company/Organization Name", value="Engineering Consultants Ltd.")
    engineer_name = st.text_input("Design Engineer", value="Senior Bridge Engineer")
    report_title = st.text_input("Report Title", value=f"Comprehensive Bridge Design Report - {st.session_state.project_data.bridge_name if st.session_state.project_data else 'Bridge Project'}")
    
    # Advanced options
    with st.expander("Advanced Report Options"):
        page_orientation = st.selectbox("Page Orientation", ["Portrait", "Landscape", "Mixed"])
        font_size = st.selectbox("Font Size", ["10pt", "11pt", "12pt"], index=1)
        include_appendix = st.checkbox("Include Excel Formula Appendix", value=True)
        include_code_refs = st.checkbox("Include Code References", value=True)
        watermark_text = st.text_input("Watermark Text (optional)", placeholder="DRAFT / CONFIDENTIAL / etc.")
    
    if st.button("Generate Report"):
        with st.spinner("Generating comprehensive report... This may take a few minutes for 250+ page reports."):
            try:
                # Initialize PDF generator
                pdf_generator = PDFGenerator()
                
                # Prepare report configuration
                report_config = {
                    'type': report_type,
                    'include_sections': include_sections,
                    'output_format': output_format,
                    'include_calculations': include_calculations,
                    'include_drawings': include_drawings,
                    'include_photos': include_photos,
                    'company_name': company_name,
                    'engineer_name': engineer_name,
                    'report_title': report_title,
                    'page_orientation': page_orientation,
                    'font_size': font_size,
                    'include_appendix': include_appendix,
                    'include_code_refs': include_code_refs,
                    'watermark_text': watermark_text
                }
                
                # Compile all data for report
                report_data = {
                    'project_data': st.session_state.project_data.__dict__ if st.session_state.project_data else {},
                    'analysis_results': st.session_state.analysis_results,
                    'excel_files': st.session_state.excel_files,
                    'claude_validations': getattr(st.session_state, 'claude_validations', {}),
                    'config': report_config
                }
                
                # Generate report
                if output_format == "PDF":
                    report_buffer = pdf_generator.generate_comprehensive_pdf(report_data)
                elif output_format == "HTML":
                    report_buffer = pdf_generator.generate_html_report(report_data)
                else:  # Word Document
                    report_buffer = pdf_generator.generate_word_report(report_data)
                
                st.success("✅ Report generated successfully!")
                
                # Report statistics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Report Size", f"{len(report_buffer.getvalue()) / 1024 / 1024:.1f} MB")
                
                with col2:
                    estimated_pages = pdf_generator.get_estimated_page_count(report_data)
                    st.metric("Estimated Pages", f"{estimated_pages}")
                
                with col3:
                    st.metric("Sections Included", f"{len(include_sections)}")
                
                # Download button
                file_extension = {"PDF": "pdf", "HTML": "html", "Word Document": "docx"}[output_format]
                mime_types = {
                    "PDF": "application/pdf",
                    "HTML": "text/html",
                    "Word Document": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                }
                
                st.download_button(
                    label=f"📄 Download {output_format} Report",
                    data=report_buffer.getvalue(),
                    file_name=f"Bridge_Design_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_extension}",
                    mime=mime_types[output_format]
                )
                
                # Preview section
                if output_format == "HTML":
                    st.subheader("Report Preview")
                    with st.expander("HTML Preview (First 2000 characters)", expanded=False):
                        preview_content = report_buffer.getvalue().decode('utf-8')[:2000]
                        st.code(preview_content, language="html")
                
                # Report summary
                st.subheader("Report Generation Summary")
                
                generation_summary = pdf_generator.get_generation_summary(report_data)
                
                st.write("**Content Summary:**")
                if 'content_summary' in generation_summary:
                    for section, details in generation_summary['content_summary'].items():
                        st.write(f"- {section}: {details}")
                
                st.write("**Technical Details:**")
                if 'technical_summary' in generation_summary:
                    for detail, value in generation_summary['technical_summary'].items():
                        st.write(f"- {detail}: {value}")
                
                # Additional report options
                st.subheader("Additional Report Options")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("Generate Executive Summary"):
                        exec_config = report_config.copy()
                        exec_config['type'] = "Executive Summary"
                        exec_config['include_sections'] = ["Project Overview", "Key Results", "Recommendations"]
                        
                        exec_buffer = pdf_generator.generate_executive_summary(report_data, exec_config)
                        
                        st.download_button(
                            label="📋 Download Executive Summary",
                            data=exec_buffer.getvalue(),
                            file_name=f"Executive_Summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf"
                        )
                
                with col2:
                    if st.button("Generate Calculation Sheets"):
                        calc_buffer = pdf_generator.generate_calculation_sheets(report_data)
                        
                        st.download_button(
                            label="🔢 Download Calculation Sheets",
                            data=calc_buffer.getvalue(),
                            file_name=f"Calculation_Sheets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf"
                        )
                
            except Exception as e:
                st.error(f"❌ Error generating report: {str(e)}")
                st.exception(e)

if __name__ == "__main__":
    main()
