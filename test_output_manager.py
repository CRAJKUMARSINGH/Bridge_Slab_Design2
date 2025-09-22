#!/usr/bin/env python3
"""
Test script for OutputManager module
"""

import sys
import os
import tempfile
from pathlib import Path

# Add the current directory to the path to import modules
sys.path.insert(0, os.path.dirname(__file__))

try:
    from utils.output_manager import OutputManager
    print("✅ Successfully imported OutputManager")
except ImportError as e:
    print(f"❌ Failed to import OutputManager: {e}")
    sys.exit(1)

def test_output_manager():
    """Test the OutputManager class"""
    print("Testing OutputManager...")
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize output manager with temp directory
        output_manager = OutputManager(temp_dir)
        
        # Test creating output paths
        print("\n1. Testing path creation...")
        path1 = output_manager.create_output_path("Submersible Bridge", "pdf")
        print(f"   Path 1: {path1}")
        
        path2 = output_manager.create_output_path("High Level Bridge", "pdf")
        print(f"   Path 2: {path2}")
        
        path3 = output_manager.create_output_path("Submersible Bridge", "pdf")  # Same date, same type
        print(f"   Path 3: {path3}")
        
        # Test saving files
        print("\n2. Testing file saving...")
        test_content = b"This is a test PDF content"
        
        saved_path1 = output_manager.save_output_file(test_content, "Submersible Bridge", "pdf")
        print(f"   Saved file 1: {saved_path1}")
        
        saved_path2 = output_manager.save_output_file(test_content, "High Level Bridge", "pdf")
        print(f"   Saved file 2: {saved_path2}")
        
        # Test directory structure
        print("\n3. Testing directory structure...")
        tree = output_manager.get_output_directory_tree()
        print(f"   Directory tree: {tree}")
        
        # Verify files exist
        if saved_path1.exists() and saved_path2.exists():
            print("✅ All tests passed!")
            return True
        else:
            print("❌ File saving test failed!")
            return False

if __name__ == "__main__":
    success = test_output_manager()
    sys.exit(0 if success else 1)