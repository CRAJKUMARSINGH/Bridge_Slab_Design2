#!/usr/bin/env python3
"""
Script to generate sample outputs to demonstrate the organized folder system
"""

import sys
import os
from pathlib import Path

# Add the current directory to the path to import modules
sys.path.insert(0, os.path.dirname(__file__))

try:
    from utils.output_manager import OutputManager
    print("✅ Successfully imported OutputManager")
except ImportError as e:
    print(f"❌ Failed to import OutputManager: {e}")
    sys.exit(1)

def generate_sample_outputs():
    """Generate sample outputs to demonstrate the folder system"""
    print("Generating sample outputs...")
    
    # Initialize output manager
    output_manager = OutputManager()
    
    # Sample content for different file types
    pdf_content = b"%PDF-1.4 Sample PDF Content"
    html_content = b"<html><body><h1>Sample HTML Report</h1></body></html>"
    docx_content = b"PK\x03\x04 Sample DOCX Content"
    
    # Generate sample outputs for different bridge types
    bridge_types = [
        "Submersible Bridge",
        "High Level Bridge", 
        "Aqueduct",
        "Culvert"
    ]
    
    file_types = [
        ("pdf", pdf_content),
        ("html", html_content),
        ("docx", docx_content)
    ]
    
    # Create sample outputs
    for i, bridge_type in enumerate(bridge_types):
        for j, (ext, content) in enumerate(file_types):
            try:
                saved_path = output_manager.save_output_file(content, bridge_type, ext)
                print(f"✅ Created: {saved_path}")
            except Exception as e:
                print(f"❌ Error creating output for {bridge_type}.{ext}: {e}")
    
    # Show directory structure
    print("\n📁 Output Directory Structure:")
    tree = output_manager.get_output_directory_tree()
    for date, bridge_data in tree.items():
        print(f"  {date}/")
        for bridge_type, files in bridge_data.items():
            print(f"    {bridge_type}/")
            for file in files:
                print(f"      {file}")
    
    print(f"\n✅ Sample outputs generated successfully in the 'outputs' directory!")

if __name__ == "__main__":
    generate_sample_outputs()