"""
Output Manager Module
Handles organized storage of generated reports and files in date-based subfolders
with bridge type and serial numbering system.
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

class OutputManager:
    """Manages organized storage of output files"""
    
    def __init__(self, base_output_dir: str = "outputs"):
        """
        Initialize OutputManager
        
        Args:
            base_output_dir (str): Base directory for all outputs
        """
        self.base_output_dir = Path(base_output_dir)
        self.base_output_dir.mkdir(exist_ok=True)
        self.metadata_file = self.base_output_dir / "output_metadata.json"
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict[str, Any]:
        """
        Load metadata from file or create new if doesn't exist
        
        Returns:
            Dict[str, Any]: Metadata dictionary
        """
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _save_metadata(self):
        """Save metadata to file"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save metadata: {e}")
    
    def _get_next_serial_number(self, date_str: str, bridge_type: str) -> int:
        """
        Get the next serial number for a given date and bridge type
        
        Args:
            date_str (str): Date in YYYY-MM-DD format
            bridge_type (str): Bridge type
            
        Returns:
            int: Next serial number
        """
        key = f"{date_str}_{bridge_type}"
        if key not in self.metadata:
            self.metadata[key] = 0
        
        self.metadata[key] += 1
        self._save_metadata()
        return self.metadata[key]
    
    def create_output_path(self, bridge_type: str, file_extension: str = "pdf") -> Path:
        """
        Create an organized output path with date, bridge type, and serial number
        
        Args:
            bridge_type (str): Type of bridge (e.g., "Submersible Bridge", "High Level Bridge")
            file_extension (str): File extension (without dot)
            
        Returns:
            Path: Complete path for the output file
        """
        # Clean bridge type for folder naming (remove spaces, special chars)
        clean_bridge_type = "".join(c for c in bridge_type if c.isalnum() or c in "._- ").strip()
        clean_bridge_type = "_".join(clean_bridge_type.split())
        
        # Get current date
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        
        # Get next serial number
        serial_number = self._get_next_serial_number(date_str, clean_bridge_type)
        
        # Create date-based subfolder
        date_folder = self.base_output_dir / date_str
        date_folder.mkdir(exist_ok=True)
        
        # Create bridge type subfolder within date folder
        bridge_folder = date_folder / clean_bridge_type
        bridge_folder.mkdir(exist_ok=True)
        
        # Create filename with timestamp and serial number
        timestamp = now.strftime("%H%M%S")
        filename = f"{date_str}_{clean_bridge_type}_{serial_number:03d}_{timestamp}.{file_extension}"
        
        return bridge_folder / filename
    
    def save_output_file(self, content: bytes, bridge_type: str, file_extension: str = "pdf") -> Path:
        """
        Save output file to organized directory structure
        
        Args:
            content (bytes): File content as bytes
            bridge_type (str): Type of bridge
            file_extension (str): File extension (without dot)
            
        Returns:
            Path: Path where file was saved
        """
        output_path = self.create_output_path(bridge_type, file_extension)
        
        try:
            with open(output_path, 'wb') as f:
                f.write(content)
            
            print(f"✅ Output saved to: {output_path}")
            return output_path
        except Exception as e:
            print(f"❌ Error saving output file: {e}")
            raise
    
    def get_output_directory_tree(self) -> Dict[str, Any]:
        """
        Get a tree representation of the output directory structure
        
        Returns:
            Dict[str, Any]: Directory tree structure
        """
        tree = {}
        
        for date_folder in sorted(self.base_output_dir.iterdir()):
            if date_folder.is_dir() and date_folder.name != ".git":
                tree[date_folder.name] = {}
                for bridge_folder in sorted(date_folder.iterdir()):
                    if bridge_folder.is_dir():
                        files = sorted([f.name for f in bridge_folder.iterdir() if f.is_file()])
                        tree[date_folder.name][bridge_folder.name] = files
        
        return tree
    
    def list_outputs_by_date(self, date_str: str) -> Dict[str, list]:
        """
        List all outputs for a specific date
        
        Args:
            date_str (str): Date in YYYY-MM-DD format
            
        Returns:
            Dict[str, list]: Bridge types and their files
        """
        date_folder = self.base_output_dir / date_str
        if not date_folder.exists():
            return {}
        
        result = {}
        for bridge_folder in sorted(date_folder.iterdir()):
            if bridge_folder.is_dir():
                files = sorted([f.name for f in bridge_folder.iterdir() if f.is_file()])
                result[bridge_folder.name] = files
        
        return result

# Example usage:
if __name__ == "__main__":
    # Example of how to use the OutputManager
    output_manager = OutputManager()
    
    # Create a sample output path
    path = output_manager.create_output_path("Submersible Bridge", "pdf")
    print(f"Example output path: {path}")
    
    # Show directory structure
    tree = output_manager.get_output_directory_tree()
    print(f"Directory structure: {tree}")