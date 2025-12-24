#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration and constants for the Synthetic Identity Generator.
Contains color definitions, paths, and global settings.
"""

from pathlib import Path

# ============================================================================
# COLOR DEFINITIONS
# ============================================================================
BOLD = '\033[1m'
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
PURPLE = MAGENTA
CYAN = '\033[96m'
WHITE = '\033[97m'
RESET = '\033[0m'

# ============================================================================
# PATHS
# ============================================================================
# Base directory (project root)
BASE_DIR = Path(__file__).resolve().parent.parent

# Data directories
DATA_DIR = BASE_DIR / "data"
COUNTRIES_DIR = DATA_DIR / "countries"
IDENTITIES_DIR = DATA_DIR / "identities"
JOBS_FILE = DATA_DIR / "jobs.txt"
HOBBIES_FILE = DATA_DIR / "hobbies.txt"

# ============================================================================
# BOX DISPLAY SETTINGS
# ============================================================================
BOX_WIDTH = 100
CONTENT_WIDTH = BOX_WIDTH - 4  # 96 characters for content

# ============================================================================
# EMAIL SETTINGS
# ============================================================================
EMAIL_DOMAIN = "1secmail.com"
EMAIL_API_BASE = "https://www.1secmail.com/api/v1/"
