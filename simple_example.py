#!/usr/bin/env python3
"""
Simple Example - Clinical Trial Matcher with MCP

This is the simplest possible usage of the Clinical Trial Matcher.
Perfect for getting started quickly. Now uses the MCP server to query
ClinicalTrials.gov in real-time.
"""

import os
from dotenv import load_dotenv
from clinical_trial_matcher import ClinicalTrialMatcher

# Load your API key from .env file
load_dotenv()

# Simple patient data (deidentified)
patient = """
62 year old male with Stage IV non-small cell lung cancer.
PD-L1 expression: 65%
ECOG performance status: 1
Prior treatment: carboplatin/pemetrexed (completed)
Labs: Normal organ function
No brain metastases
No autoimmune disease
"""

# Initialize matcher with MCP server
print("Connecting to ClinicalTrials.gov via MCP server...")
matcher = ClinicalTrialMatcher(
    mcp_server_url="https://clinicaltrialsgov-mcp.onrender.com"
)

# Find matching trials
print("Searching and analyzing trials...")
matches = matcher.match_patient_to_trials(patient)

# Show results
print(f"\nFound {len(matches)} matching trials\n")

for match in matches[:3]:  # Top 3
    print(f"✓ {match.trial_name}")
    print(f"  Trial ID: {match.trial_id}")
    print(f"  Status: {match.match_status}")
    print(f"  Confidence: {match.confidence_score:.0%}")
    print(f"  Contact: {match.contact_info}")
    print()

