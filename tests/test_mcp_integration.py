#!/usr/bin/env python3
"""
Test script for MCP integration with ClinicalTrials.gov
This script tests the connection to the MCP server and basic functionality.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clinical_trial_matcher import ClinicalTrialMatcher

# Load environment variables
load_dotenv()

def test_mcp_connection():
    """Test basic MCP server connection"""
    print("=" * 80)
    print("TEST 1: MCP Server Connection")
    print("=" * 80)
    
    try:
        matcher = ClinicalTrialMatcher(
            mcp_server_url="https://clinicaltrialsgov-mcp.onrender.com"
        )
        print("✓ Successfully initialized ClinicalTrialMatcher with MCP server")
        return matcher
    except Exception as e:
        print(f"✗ Failed to initialize: {str(e)}")
        return None

def test_condition_extraction(matcher):
    """Test condition extraction from patient data"""
    print("\n" + "=" * 80)
    print("TEST 2: Condition Extraction")
    print("=" * 80)
    
    patient_data = """
    Patient is a 62 year old male with Stage IV non-small cell lung cancer.
    PD-L1 expression: 65%
    ECOG performance status: 1
    """
    
    try:
        conditions = matcher._extract_conditions_from_patient_data(patient_data)
        print(f"✓ Extracted conditions: {conditions}")
        return conditions
    except Exception as e:
        print(f"✗ Failed to extract conditions: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def test_trial_search(matcher, conditions):
    """Test searching for trials via MCP"""
    print("\n" + "=" * 80)
    print("TEST 3: Trial Search via MCP")
    print("=" * 80)
    
    if not conditions:
        conditions = ["lung cancer"]
    
    try:
        trial_ids = matcher._search_trials_via_mcp(conditions, max_studies=5)
        print(f"✓ Found {len(trial_ids)} trials: {trial_ids[:3]}...")
        return trial_ids
    except Exception as e:
        print(f"✗ Failed to search trials: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def test_trial_details(matcher, trial_ids):
    """Test retrieving trial details via MCP"""
    print("\n" + "=" * 80)
    print("TEST 4: Retrieve Trial Details")
    print("=" * 80)
    
    if not trial_ids:
        print("✗ No trial IDs available to test")
        return False
    
    try:
        trial_id = trial_ids[0]
        print(f"Retrieving details for: {trial_id}")
        trial = matcher._get_trial_details_via_mcp(trial_id)
        
        if trial:
            print(f"✓ Successfully retrieved trial details")
            print(f"  Trial ID: {trial['trial_id']}")
            print(f"  Trial Name: {trial['trial_name']}")
            print(f"  Full text length: {len(trial['full_text'])} characters")
            return True
        else:
            print("✗ Failed to retrieve trial details")
            return False
    except Exception as e:
        print(f"✗ Error retrieving trial details: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_full_matching(matcher):
    """Test the complete matching workflow"""
    print("\n" + "=" * 80)
    print("TEST 5: Full Matching Workflow")
    print("=" * 80)
    
    patient_data = """
    Patient is a 62 year old male with Stage IV non-small cell lung cancer.
    PD-L1 expression: 65%
    ECOG performance status: 1
    Prior treatment: carboplatin/pemetrexed (completed)
    Labs: Normal organ function
    No brain metastases
    No autoimmune disease
    """
    
    try:
        print("Running full matching workflow (this may take 2-3 minutes)...")
        matches = matcher.match_patient_to_trials(
            patient_data,
            max_trials_to_return=3  # Only get top 3 for testing
        )
        
        print(f"\n✓ Successfully completed matching")
        print(f"  Found {len(matches)} matches")
        
        if matches:
            print("\nTop match:")
            match = matches[0]
            print(f"  Trial: {match.trial_name}")
            print(f"  ID: {match.trial_id}")
            print(f"  Status: {match.match_status}")
            print(f"  Confidence: {match.confidence_score:.1%}")
            print(f"  Reasoning: {match.reasoning[:200]}...")
        
        return True
    except Exception as e:
        print(f"✗ Failed full matching: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("MCP INTEGRATION TEST SUITE")
    print("Testing ClinicalTrials.gov MCP Server Integration")
    print("=" * 80)
    
    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("\n✗ ERROR: ANTHROPIC_API_KEY not found")
        print("Please set it in your .env file or export it:")
        print("  export ANTHROPIC_API_KEY='your-api-key-here'")
        sys.exit(1)
    
    # Test 1: Connection
    matcher = test_mcp_connection()
    if not matcher:
        print("\n✗ Cannot proceed without MCP connection")
        sys.exit(1)
    
    # Test 2: Condition extraction
    conditions = test_condition_extraction(matcher)
    
    # Test 3: Trial search
    trial_ids = test_trial_search(matcher, conditions)
    
    # Test 4: Trial details
    test_trial_details(matcher, trial_ids)
    
    # Test 5: Full matching (optional - takes time)
    print("\n" + "=" * 80)
    response = input("Run full matching test? (takes 2-3 minutes) [y/N]: ")
    if response.lower() == 'y':
        test_full_matching(matcher)
    else:
        print("Skipping full matching test")
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUITE COMPLETE")
    print("=" * 80)
    print("\nIf all tests passed, the MCP integration is working correctly!")
    print("You can now use the application with live ClinicalTrials.gov data.")
    print("\nNext steps:")
    print("  1. Run the web server: ./run.sh")
    print("  2. Try the simple example: python simple_example.py")
    print("  3. Run the demo: python demo_matcher.py")

if __name__ == "__main__":
    main()

