"""
RQ1 Agent Configuration
Contains constants and configuration values used across the application.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# RQ1 Tool Identification
# These values identify this tool to RQ1 servers for logging/auditing purposes
RQ1_TOOLNAME = "OfficeUtils"
RQ1_TOOLVERSION = "1.0"

# Environment
# Use PRODUCTIVE for real data, ACCEPTANCE for testing
RQ1_ENVIRONMENT = "PRODUCTIVE"  # Options: "PRODUCTIVE", "ACCEPTANCE"

# Project Configuration
# Project RQ1 IDs for validation scope (comma-separated list)
# Examples: "RQONE12345678" or "RQONE12345678,RQONE87654321"
_project_ids_raw = os.getenv('RQ1_PROJECT_IDS', '')
RQ1_PROJECT_IDS = [pid.strip() for pid in _project_ids_raw.split(',') if pid.strip()]  # Parse comma-separated list

# Optional: comma-separated rule IDs to enable (e.g. PRPL 01,PRPL 03,PRPL 11)
# If not set, all 12 rules are applied
_rules_raw = os.getenv('RQ1_RULES', '')
RQ1_ENABLED_RULES = set(r.strip() for r in _rules_raw.split(',') if r.strip()) or None

# Optional: comma-separated NTIDs of team members to validate
# If not set, only validates the owner (RQ1_USER) unless a CLI argument is given
_members_raw = os.getenv('RQ1_MEMBERS', '')
RQ1_MEMBERS = [m.strip() for m in _members_raw.split(',') if m.strip()]
