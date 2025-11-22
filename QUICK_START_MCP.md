# Quick Start Guide - MCP Integration

## 🚀 Your Clinical Trial Qualifier is now MCP-enabled!

The system now queries **ClinicalTrials.gov** in real-time using Model Context Protocol (MCP).

## What This Means

Instead of reading from a static file with 6 trials, your system now:
- ✅ Accesses **400,000+ live clinical trials**
- ✅ Gets **real-time, up-to-date information**
- ✅ Uses **Claude to intelligently search** based on patient conditions
- ✅ Provides **more relevant matches** automatically

## Quick Test (2 minutes)

### Test 1: Verify MCP Integration

```bash
python test_mcp_integration.py
```

**What it tests:**
- MCP server connection ✓
- Claude condition extraction ✓
- ClinicalTrials.gov search ✓
- Trial detail retrieval ✓

**Expected output:**
```
✓ Successfully initialized ClinicalTrialMatcher with MCP server
✓ Extracted conditions: ['lung cancer', 'stage IV', 'non-small cell']
✓ Found 15 trials: ['NCT12345678', 'NCT87654321', ...]
✓ Successfully retrieved trial details
```

### Test 2: Run Simple Example

```bash
python simple_example.py
```

**What it does:**
- Searches for lung cancer trials
- Evaluates patient eligibility
- Shows top 3 matches

**Expected time:** ~2-3 minutes (queries live API)

## Full Demo (10 minutes)

Test with multiple patient types:

```bash
python demo_matcher.py
```

Tests three patients:
1. **NSCLC Patient** - searches lung cancer trials
2. **Type 2 Diabetes Patient** - searches diabetes trials
3. **Alzheimer's Patient** - searches Alzheimer's trials

## Web Application

Start the web server:

```bash
./run.sh
```

Visit: **http://localhost:5000**

Now when you:
1. Enter patient information
2. Click "De-identify and Match Trials"
3. The system will:
   - Extract PHI using Skyflow ✓
   - Identify medical conditions using Claude ✓
   - Search ClinicalTrials.gov via MCP ✓
   - Evaluate eligibility for each trial ✓
   - Return ranked matches ✓

## How It Works Now

### Old Workflow (Static)
```
Patient Data → Match against 6 static trials → Results
```

### New Workflow (MCP + Live)
```
Patient Data
    ↓
Extract Conditions (Claude)
    ↓
Search ClinicalTrials.gov (MCP)
    ↓
Retrieve Trial Details (MCP)
    ↓
Evaluate Eligibility (Claude)
    ↓
Ranked Results
```

## Example Usage

### Python Script

```python
from clinical_trial_matcher import ClinicalTrialMatcher

# Initialize with MCP
matcher = ClinicalTrialMatcher()

# Patient data
patient = """
65 year old with metastatic breast cancer.
HER2 positive
Prior treatment: chemotherapy, trastuzumab
ECOG status: 1
"""

# Find trials (queries ClinicalTrials.gov)
matches = matcher.match_patient_to_trials(patient)

# Display results
for match in matches[:5]:
    print(f"Trial: {match.trial_name}")
    print(f"Status: {match.match_status}")
    print(f"Confidence: {match.confidence_score:.0%}")
    print()
```

### cURL (API)

```bash
curl -X POST http://localhost:5000/match_trials \
  -H "Content-Type: application/json" \
  -d '{
    "deidentified_text": "65 year old with metastatic breast cancer...",
    "max_trials": 10
  }'
```

## Understanding Results

### Match Statuses

- **QUALIFIED** ✅: Patient meets main criteria, good candidate
- **NOT_QUALIFIED** ❌: Clear mismatch (wrong condition, major exclusion)
- **NEEDS_MORE_INFO** ⚠️: Could match but missing critical data

### Confidence Scores

- **80-100%**: Strong match, highly recommended
- **60-79%**: Good match, consider carefully
- **40-59%**: Possible match, review details
- **<40%**: Weak match, may not be suitable

### Sample Output

```
================================================================================
CLINICAL TRIAL MATCHING REPORT
================================================================================

Total Trials Evaluated: 8
Qualified: 3
Not Qualified: 4
Needs More Information: 1

--------------------------------------------------------------------------------

1. Phase III Study of Novel CDK4/6 Inhibitor in HR+/HER2- Breast Cancer
   Trial ID: NCT04123456
   Status: QUALIFIED
   Confidence: 85.00%
   Contact: clinicaltrials@hospital.org | Phone: 1-800-555-0123

   ✓ Inclusion Criteria Met (7):
     • Age 18 or older
     • Histologically confirmed breast cancer
     • HR+/HER2- disease
     • Metastatic disease
     • Prior chemotherapy
     • ECOG 0-1
     • Adequate organ function

   Reasoning:
     Patient meets all major inclusion criteria. Disease subtype matches
     (HR+/HER2-), and performance status is appropriate. Prior treatment
     history aligns with study requirements.
```

## Common Issues

### MCP Server Timeout

**Problem:** First request takes 30+ seconds

**Solution:** This is normal - Render free tier "cold starts"
- Wait 30-60 seconds
- Subsequent requests will be faster

### No Trials Found

**Problem:** Search returns 0 results

**Solutions:**
- Ensure patient data includes clear medical condition
- Check extracted conditions in console output
- Try with more common condition terms
- Verify internet connectivity

### Slow Performance

**Normal timing:**
- First trial evaluation: ~30-40s (includes MCP cold start)
- Subsequent trials: ~15-20s each
- Total for 10 trials: ~2-4 minutes

**To speed up:**
- Reduce `max_trials_to_return` to 5
- Use after MCP server is "warm"

## MCP Server Details

**URL:** https://clinicaltrialsgov-mcp.onrender.com

**Tools:**
1. `list_studies` - Search by condition
2. `get_study` - Get trial details by NCT ID

**Data Source:** ClinicalTrials.gov official API

**Update Frequency:** Real-time (always current)

## Customization

### Change MCP Server

```python
matcher = ClinicalTrialMatcher(
    mcp_server_url="https://your-mcp-server.com"
)
```

### Adjust Number of Trials

```python
matches = matcher.match_patient_to_trials(
    patient_data,
    max_trials_to_return=5  # Default: 10
)
```

### Add Progress Callback

```python
def progress(msg):
    print(f"Progress: {msg}")

matches = matcher.match_patient_to_trials(
    patient_data,
    progress_callback=progress
)
```

## Next Steps

1. ✅ **Test MCP integration**: Run `test_mcp_integration.py`
2. ✅ **Try simple example**: Run `simple_example.py`
3. ✅ **Run full demo**: Run `demo_matcher.py`
4. ✅ **Start web app**: Run `./run.sh`
5. 📖 **Read documentation**: See `README.md` and `MCP_MIGRATION_GUIDE.md`

## Resources

- **Full Documentation**: [README.md](README.md)
- **Migration Guide**: [MCP_MIGRATION_GUIDE.md](MCP_MIGRATION_GUIDE.md)
- **Change Summary**: [CHANGES_SUMMARY.md](CHANGES_SUMMARY.md)
- **API Docs**: http://localhost:5000/docs (when server is running)

## Support

For issues:
1. Check logs/console output
2. Verify MCP server accessibility
3. Test with `test_mcp_integration.py`
4. Review troubleshooting in README.md

---

**You're all set!** 🎉

Your Clinical Trial Qualifier now has real-time access to ClinicalTrials.gov through MCP.

Start with: `python test_mcp_integration.py`

