#!/usr/bin/env python3
"""
Generate a CSV index of all vocabulary JSON configuration files.
"""

import json
import csv
import os
import argparse
from pathlib import Path
from datetime import datetime

# Configuration
REPO_ROOT = Path(__file__).parent.parent.parent
JSON_PATTERN = "*.json"
EXCLUDE_DIRS = {".git", ".github", ".venv", "venv"}

# CSV column headers
CSV_HEADERS = [
    "id",
    "filename",
    "url",
    "label",
    "namespaceUri",
    "prefix",
    "format",
    "comment",
    "last_modified"
]

def should_exclude_path(path: Path) -> bool:
    """Check if path should be excluded from indexing."""
    for part in path.parts:
        if part in EXCLUDE_DIRS:
            return True
    return False


def find_json_files(root: Path) -> list:
    """Find all JSON files in the repository (excluding certain directories)."""
    json_files = []
    
    for json_file in root.rglob(JSON_PATTERN):
        if not should_exclude_path(json_file):
            json_files.append(json_file)
    
    return sorted(json_files)


def extract_metadata(json_file: Path) -> dict|None:
    """Extract metadata from a JSON configuration file."""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Create relative path for ID (without extension)
        relative_path = json_file.relative_to(REPO_ROOT)
        file_id = str(relative_path.with_suffix(''))
        
        # Get file modification time
        mod_time = datetime.fromtimestamp(json_file.stat().st_mtime).isoformat()
        
        metadata = {
            "id": file_id,
            "filename": json_file.name,
            "url": data.get("url", ""),
            "label": data.get("label", ""),
            "namespaceUri": data.get("namespaceUri", ""),
            "prefix": data.get("prefix", ""),
            "format": data.get("format", ""),
            "comment": data.get("comment", ""),
            "last_modified": mod_time,
        }
        
        return metadata
    
    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Could not read {json_file}: {e}")
        return None


def generate_index(output_file: Path):
    """Generate the CSV index file."""
    # Create output directory if it doesn't exist
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Find all JSON files
    json_files = find_json_files(REPO_ROOT)
    
    # Output message if no files found
    if not json_files:
        print("No JSON files found to index.")
    
    # Extract metadata from each file
    records = []
    for json_file in json_files:
        metadata = extract_metadata(json_file)
        if metadata:
            records.append(metadata)
    
    # Write CSV file
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=CSV_HEADERS)
        writer.writeheader()
        writer.writerows(records)
    
    print(f"✓ Generated index with {len(records)} vocabulary configuration(s)")
    print(f"✓ Index saved to: {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a CSV index of all vocabulary JSON configuration files."
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=Path("vocabulary_index.csv"),
        help="Output CSV file path (default: vocabulary_index.csv in current directory)"
    )
    
    args = parser.parse_args()
    generate_index(args.output)
