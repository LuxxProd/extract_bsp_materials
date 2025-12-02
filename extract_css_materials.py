#!/usr/bin/env python3
"""
extract_css_materials.py

Extracts materials from a CS:S original map BSP pakfile and creates
an addon that clients can install to see original textures on stripped maps.

Usage:
    python extract_css_materials.py "path/to/original/cs_assault.bsp" "output_addon_folder"
"""

import io
import sys
import zipfile
from pathlib import Path


def find_pak_bounds(data: bytes):
    """Find pakfile bounds in BSP."""
    start = data.find(b"PK\x03\x04")
    if start == -1:
        return None, None
    eocd = data.rfind(b"PK\x05\x06")
    if eocd == -1:
        return None, None
    if eocd + 22 > len(data):
        return None, None
    comment_len = int.from_bytes(data[eocd + 20 : eocd + 22], "little")
    archive_end = eocd + 22 + comment_len
    return start, archive_end





def extract_materials_to_addon(bsp_path: Path, output_dir: Path, quiet=False):
    """Extract all materials from BSP pakfile to addon structure."""
    try:
        data = bsp_path.read_bytes()
        pak_start, pak_end = find_pak_bounds(data)
        
        if pak_start is None:
            if not quiet:
                print(f"  No pakfile found in {bsp_path.name}")
            return False
        
        pakfile_data = data[pak_start:pak_end]
        
        # Parse pakfile
        with zipfile.ZipFile(io.BytesIO(pakfile_data), 'r') as zf:
            material_files = [name for name in zf.namelist() 
                            if name.startswith('materials/') and not name.endswith('/')]
            
            if not material_files:
                if not quiet:
                    print(f"  No materials found in pakfile")
                return False
            
            if not quiet:
                print(f"  Found {len(material_files)} material files")
            
            # Extract to addon structure - keep VMTs as-is with includes
            # Client must have CS:S mounted for includes to work
            for file_path in material_files:
                content = zf.read(file_path)
                out_path = output_dir / file_path
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_bytes(content)
        
        # Create addon.json
        map_name = bsp_path.stem
        addon_json = output_dir / "addon.json"
        addon_json.write_text(f'''{{\n    "title": "CS:S {map_name} Materials",\n    "type": "effects",\n    "tags": [ "scenic" ]\n}}''')
        
        if not quiet:
            print(f"  ✓ Created: {output_dir.name}/")
        return True
        
    except Exception as e:
        if not quiet:
            print(f"  ✗ Error: {e}")
        return False


def main(argv):
    if len(argv) != 3:
        print("Usage: python extract_css_materials.py original.bsp output_addon_folder")
        print("       python extract_css_materials.py 'input/*.bsp' 'output/css_*_materials'")
        return 2
    
    in_pattern = argv[1]
    out_pattern = argv[2]
    
    # Check if input contains wildcards
    if '*' in in_pattern or '?' in in_pattern:
        # Glob pattern mode
        import glob
        in_files = [Path(p) for p in glob.glob(in_pattern)]
        
        if not in_files:
            print(f"No files matched pattern: {in_pattern}")
            return 2
        
        # Determine base output directory
        out_base = Path(out_pattern).parent if '*' in out_pattern else Path(out_pattern)
        out_base.mkdir(parents=True, exist_ok=True)
        
        print(f"Found {len(in_files)} files")
        print(f"Output base: {out_base}")
        print()
        
        success = 0
        for in_file in in_files:
            print(f"Processing: {in_file.name}")
            addon_name = f"css_{in_file.stem}_materials"
            addon_dir = out_base / addon_name
            
            if extract_materials_to_addon(in_file, addon_dir, quiet=False):
                success += 1
        
        print()
        print(f"Completed: {success}/{len(in_files)} material addons created")
        return 0 if success > 0 else 1
    
    # Single file mode
    bsp_path = Path(in_pattern)
    output_dir = Path(out_pattern)
    
    if not bsp_path.exists():
        print(f"BSP not found: {bsp_path}")
        return 2
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if extract_materials_to_addon(bsp_path, output_dir):
        print("\nSuccess! Clients can install this addon to see original textures.")
        return 0
    return 1


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
