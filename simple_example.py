#!/usr/bin/env python3
"""
Simple Example - Clinical Trial Matcher

This is the simplest possible usage of the Clinical Trial Matcher.
Perfect for getting started quickly.
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

# Initialize matcher
matcher = ClinicalTrialMatcher(trials_file_path="clinical_trials.txt")

# Find matching trials
print("Finding matching trials...")
matches = matcher.match_patient_to_trials(patient)

# Show results
print(f"\nFound {len(matches)} trials\n")

for match in matches[:3]:  # Top 3
    print(f"✓ {match.trial_name}")
    print(f"  Status: {match.match_status}")
    print(f"  Confidence: {match.confidence_score:.0%}")
    print(f"  Contact: {match.contact_info}")
    print()

