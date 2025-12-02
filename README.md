# extract_bsp_materials

A Python tool to extract materials from BSP files. This restores original textures on stripped maps by extracting materials from the original map files.

## Features

- Extract materials from single BSP files
- Batch process multiple maps using wildcards
- Preserves VMT includes

## Requirements

- Python 3.6 or higher
- Counter-Strike: Source installed

## Usage

### Extract a Single Map

```bash
python extract_materials.py "C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Source\cstrike\maps\cs_assault.bsp" "C:\Program Files (x86)\Steam\steamapps\common\GarrysMod\garrysmod\addons\css_cs_assault_materials"
```

This creates an addon folder with the following structure:
```
css_cs_assault_materials/
├── addon.json
└── materials/
    └── (extracted textures)
```

### Batch Extract All Maps

```bash
python extract_materials.py "C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Source\cstrike\maps\*.bsp" "C:\Program Files (x86)\Steam\steamapps\common\GarrysMod\garrysmod\addons\css_*_materials"
```

This processes all BSP files in the maps folder and creates individual folders for each map.

## How It Works

1. Reads the BSP file and locates the embedded pakfile (ZIP archive)
2. Extracts all files from the `materials/` directory
3. Creates a Garry's Mod addon structure with `addon.json`
4. Preserves original VMT files with their includes intact

## Important Notes

- The tool only extracts materials; other assets (models, sounds) are not included
- Output folders are created automatically if they don't exist
