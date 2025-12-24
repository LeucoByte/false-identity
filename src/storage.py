#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Storage and file operations for the Synthetic Identity Generator.
Handles saving, loading, and deleting identity files.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List

from models import Identity
from config import IDENTITIES_DIR


def save_identity(identity: Identity, directory: str = None, filepath: str = None) -> str:
    """
    Save an identity to a JSON file.

    Args:
        identity: Identity object to save
        directory: Optional custom directory (defaults to IDENTITIES_DIR)
        filepath: Optional filepath to update existing file (overrides directory)

    Returns:
        Path to saved file as string
    """
    # If filepath is provided, update existing file
    if filepath is not None:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(identity.to_json())
        return str(filepath)

    # Otherwise, create new file with timestamp
    if directory is None:
        directory = IDENTITIES_DIR

    # Create directory if it doesn't exist
    dir_path = Path(directory)
    dir_path.mkdir(parents=True, exist_ok=True)

    # Generate filename: email_timestamp.json
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    email_clean = identity.email.replace('@', '_at_').replace('.', '_')
    filename = f"{email_clean}_{timestamp}.json"
    file_path = dir_path / filename

    # Save to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(identity.to_json())

    return str(file_path)


def load_identity(filepath: str) -> Identity:
    """
    Load an identity from a JSON file.

    Args:
        filepath: Path to JSON file

    Returns:
        Identity object

    Note:
        Handles backward compatibility by setting default email_status
        if not present in older saved files.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Backward compatibility: set defaults for missing fields
    if 'email_status' not in data:
        data['email_status'] = "Inactivated"

    if 'notes' not in data:
        data['notes'] = []

    if 'family' not in data:
        data['family'] = {
            "marital_status": "Single",
            "partner": None,
            "ex_partner": None,
            "father": None,
            "mother": None,
            "children": []
        }

    # Add father and mother to existing family data
    if 'family' in data and data['family'] is not None:
        if 'father' not in data['family']:
            data['family']['father'] = None
        if 'mother' not in data['family']:
            data['family']['mother'] = None

    if 'postal_code' not in data:
        data['postal_code'] = None

    if 'religion' not in data:
        data['religion'] = "Unknown"

    return Identity(**data)


def list_saved_identities(directory: str = None) -> List[Path]:
    """
    List all saved identity JSON files.

    Args:
        directory: Optional custom directory (defaults to IDENTITIES_DIR)

    Returns:
        List of Path objects sorted by modification time (oldest first)
    """
    if directory is None:
        directory = IDENTITIES_DIR

    dir_path = Path(directory)
    if not dir_path.exists():
        return []

    # Get all JSON files, sorted by modification time (oldest first, newest last)
    files = sorted(dir_path.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=False)
    return files


def delete_identity(filepath: Path) -> bool:
    """
    Delete a specific identity file.

    Args:
        filepath: Path to identity file

    Returns:
        True if deleted successfully, False otherwise
    """
    try:
        filepath.unlink()
        return True
    except Exception:
        return False


def clean_all_identities(directory: str = None) -> int:
    """
    Delete all saved identity files.

    Args:
        directory: Optional custom directory (defaults to IDENTITIES_DIR)

    Returns:
        Number of files deleted
    """
    if directory is None:
        directory = IDENTITIES_DIR

    files = list_saved_identities(directory)
    deleted = 0
    for filepath in files:
        if delete_identity(filepath):
            deleted += 1
    return deleted


def import_identities_from_json(json_file: str, directory: str = None) -> tuple[int, int]:
    """
    Import identities from a JSON file containing multiple identities.

    The JSON file can contain:
    - A single identity object
    - An array of identity objects
    - An object with an 'identities' key containing an array

    Args:
        json_file: Path to JSON file with identities
        directory: Optional custom directory (defaults to IDENTITIES_DIR)

    Returns:
        Tuple of (imported_count, failed_count)
    """
    if directory is None:
        directory = IDENTITIES_DIR

    imported = 0
    failed = 0

    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Determine structure
        identities_data = []

        if isinstance(data, list):
            # Array of identities
            identities_data = data
        elif isinstance(data, dict):
            if 'identities' in data:
                # Object with 'identities' key
                identities_data = data['identities']
            else:
                # Single identity object
                identities_data = [data]

        # Import each identity
        for identity_dict in identities_data:
            try:
                # Set default email_status if not present
                if 'email_status' not in identity_dict:
                    identity_dict['email_status'] = "Inactivated"

                # Create Identity object
                identity = Identity(**identity_dict)

                # Save it
                save_identity(identity, directory)
                imported += 1
            except Exception:
                failed += 1

    except Exception:
        # If file reading fails, all imports failed
        return 0, 1

    return imported, failed
