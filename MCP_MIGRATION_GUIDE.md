# MCP Integration Migration Guide

## Overview

The Clinical Trial Qualifier has been updated to use the **Model Context Protocol (MCP)** to access ClinicalTrials.gov data in real-time, replacing the static `clinical_trials.txt` file.

## What Changed

### Before (Static File)
- Trials were stored in `clinical_trials.txt`
- Limited to pre-defined trials (6 in the example)
- Data could become outdated
- Required manual updates to trial database

### After (MCP + Live API)
- Queries ClinicalTrials.gov API in real-time via MCP server
- Access to 400,000+ registered clinical trials
- Always up-to-date information
- Intelligent search based on patient conditions

## Key Improvements

1. **Live Data Access**: Real-time access to the latest clinical trial information
2. **Comprehensive Coverage**: Search across all registered trials, not just a small subset
3. **Intelligent Matching**: Claude extracts conditions from patient data and searches automatically
4. **Better Results**: More relevant trials based on actual patient conditions

## Technical Changes

### ClinicalTrialMatcher Class

**Old Initialization:**
```python
matcher = ClinicalTrialMatcher(trials_file_path="clinical_trials.txt")
```

**New Initialization:**
```python
matcher = ClinicalTrialMatcher(
    mcp_server_url="https://clinicaltrialsgov-mcp.onrender.com"
)
```

### New Workflow

1. **Condition Extraction** (`_extract_conditions_from_patient_data`)
   - Uses Claude to identify medical conditions from patient data
   - Returns search terms for ClinicalTrials.gov

2. **Trial Search** (`_search_trials_via_mcp`)
   - Calls MCP `list_studies` tool
   - Searches ClinicalTrials.gov by condition
   - Returns NCT IDs of relevant trials

3. **Trial Retrieval** (`_get_trial_details_via_mcp`)
   - Calls MCP `get_study` tool
   - Gets detailed information for each trial
   - Includes criteria, contact info, etc.

4. **Evaluation** (`_evaluate_single_trial`)
   - Same as before - uses Claude to evaluate eligibility
   - Works with MCP-retrieved trial data

### Updated Files

- ✅ `clinical_trial_matcher.py` - Core matching logic with MCP integration
- ✅ `app.py` - FastAPI endpoints updated for MCP
- ✅ `demo_matcher.py` - Demo script updated
- ✅ `simple_example.py` - Simple example updated
- ✅ `requirements.txt` - Updated Anthropic SDK to 0.74.1
- ✅ `README.md` - Documentation updated
- ✅ `test_mcp_integration.py` - New test script for MCP

### Unchanged Files

- `clinical_trials.txt` - Still present but no longer used (kept for reference)
- `templates/index.html` - Web UI unchanged
- Skyflow integration - PHI redaction unchanged

## MCP Server Details

**Server URL**: `https://clinicaltrialsgov-mcp.onrender.com`

**Available Tools**:

1. **list_studies**
   - Purpose: Search for clinical trials by condition
   - Arguments:
     - `cond`: Medical condition (string)
     - `max`: Maximum number of results (optional, default: 10)
   - Returns: List of NCT IDs

2. **get_study**
   - Purpose: Get detailed information about a specific trial
   - Arguments:
     - `nct_id`: NCT ID of the trial (e.g., "NCT12345678")
   - Returns: Detailed trial information including:
     - Title
     - Inclusion/exclusion criteria
     - Contact information
     - Study design
     - Locations

## How to Use

### 1. Testing the Integration

Run the test script to verify everything works:

```bash
python test_mcp_integration.py
```

This will test:
- MCP server connection
- Condition extraction from patient data
- Trial search via MCP
- Trial detail retrieval
- (Optional) Full matching workflow

### 2. Quick Example

```python
from clinical_trial_matcher import ClinicalTrialMatcher

# Initialize with MCP server
matcher = ClinicalTrialMatcher()

# Patient data
patient_data = """
62 year old with Stage IV lung cancer.
PD-L1 expression: 65%
ECOG status: 1
"""

# Find matching trials (queries ClinicalTrials.gov)
matches = matcher.match_patient_to_trials(patient_data)

# Display results
for match in matches:
    print(f"{match.trial_name}: {match.match_status}")
```

### 3. Web Application

The web application automatically uses MCP - no changes needed:

```bash
./run.sh
```

Then visit: http://localhost:5000

## Performance Considerations

### Timing
- **Condition Extraction**: ~5-10 seconds (Claude API call)
- **Trial Search**: ~2-5 seconds (MCP call to ClinicalTrials.gov)
- **Trial Retrieval**: ~2-5 seconds per trial (MCP call)
- **Trial Evaluation**: ~10-20 seconds per trial (Claude API call)

**Total Time**: ~2-4 minutes for complete workflow with 10 trials

### MCP Server
- Hosted on Render (free tier)
- May experience cold starts (~30 seconds initial delay)
- If experiencing timeouts, retry the request

### Rate Limiting
- ClinicalTrials.gov API has rate limits
- MCP server may implement additional limits
- System retrieves up to 20 trials, returns top 10 matches

## Troubleshooting

### MCP Connection Errors

**Problem**: Cannot connect to MCP server

**Solutions**:
1. Check internet connectivity
2. Verify MCP server URL: https://clinicaltrialsgov-mcp.onrender.com
3. Wait 30 seconds for cold start (Render free tier)
4. Check for firewall/proxy issues

### No Trials Found

**Problem**: Search returns no trials

**Solutions**:
1. Check that patient data includes clear medical conditions
2. Review extracted conditions in console output
3. Try with more specific or broader condition terms
4. Verify MCP server is returning results

### Slow Performance

**Problem**: Takes too long to complete

**Solutions**:
1. Reduce `max_trials_to_return` (default: 10)
2. First run may be slower due to MCP server cold start
3. Consider caching results for repeated queries

## Backward Compatibility

### Using the Old Static File (Not Recommended)

If you need to temporarily use the old static file approach:

1. Revert to an older version of `clinical_trial_matcher.py`
2. Or create a wrapper that reads `clinical_trials.txt` and formats it for the new system

**Note**: This is not recommended as you'll miss out on live data and comprehensive trial coverage.

## Environment Variables

No new environment variables required. The existing `.env` file works:

```bash
ANTHROPIC_API_KEY=your-api-key-here
```

Skyflow credentials remain in `app.py` (for PHI redaction).

## Benefits of MCP Integration

1. **Always Current**: No need to update trial database manually
2. **Comprehensive**: Access to all registered trials
3. **Scalable**: Works for any medical condition
4. **Maintainable**: No trial database to maintain
5. **Flexible**: Easy to switch MCP servers or add new data sources
6. **Standards-Based**: Uses Model Context Protocol (MCP) standard

## Future Enhancements

Potential improvements with MCP integration:

1. **Caching**: Cache trial search results to improve performance
2. **Parallel Processing**: Retrieve multiple trials in parallel
3. **Additional Filters**: Add location, phase, status filters to search
4. **Multiple MCP Servers**: Query multiple data sources
5. **Custom MCP Tools**: Add tools for specific trial databases

## Support

For issues or questions:
1. Check the [README.md](README.md) for detailed documentation
2. Run the test script: `python test_mcp_integration.py`
3. Review the MCP server documentation
4. Check ClinicalTrials.gov API status

## Summary

The MCP integration provides a significant upgrade to the Clinical Trial Qualifier:
- ✅ Live access to 400,000+ trials
- ✅ Always up-to-date information
- ✅ Intelligent condition-based search
- ✅ No manual database maintenance
- ✅ Standards-based architecture (MCP)

The system is now production-ready for real-world clinical trial matching!

