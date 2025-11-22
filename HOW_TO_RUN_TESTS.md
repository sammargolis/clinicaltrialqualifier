# How to Run the Test Scripts

## Quick Start

All tests should be run from the project directory with the virtual environment activated:

```bash
cd /Users/sammargolis/clinicaltrialqualifier
source venv/bin/activate
```

## Test Scripts Overview

### 1. Quick Server Status Check
**File**: `check_mcp_server.py`  
**Purpose**: Quickly check if the MCP server is online

```bash
python check_mcp_server.py
```

**What it does**:
- Checks if server responds
- Shows status (online/offline)
- Provides quick feedback

**Output**: 
- ✓ Server is ONLINE! (if working)
- ✗ Server is OFFLINE (if down)

---

### 2. Basic MCP Server Testing
**File**: `test_mcp_server.py`  
**Purpose**: Test different endpoint patterns

```bash
python test_mcp_server.py
```

**What it does**:
- Tests server health
- Tries different endpoint patterns
- Tests `list_studies` and `get_study` tools
- Shows which endpoints work

**Output**: Shows which endpoints return 200 vs 502

---

### 3. Detailed MCP Testing
**File**: `test_mcp_detailed.py`  
**Purpose**: Test different request formats

```bash
python test_mcp_detailed.py
```

**What it does**:
- Tests multiple endpoint patterns
- Tests different JSON request formats
- Tests both GET and POST requests
- Shows which format works

**Output**: Shows which request format the server accepts

---

### 4. Full Integration Test
**File**: `test_mcp_integration.py`  
**Purpose**: Test the complete workflow

```bash
python test_mcp_integration.py
```

**What it does**:
- Tests MCP connection
- Tests condition extraction
- Tests trial search
- Tests trial detail retrieval
- (Optional) Tests full matching workflow

**Output**: Step-by-step progress of the entire workflow

---

### 5. Simple Example
**File**: `simple_example.py`  
**Purpose**: Quick demo with a sample patient

```bash
python simple_example.py
```

**What it does**:
- Uses a sample lung cancer patient
- Searches for matching trials
- Shows top 3 results

**Output**: Shows matching trials with status and confidence

---

### 6. Full Demo
**File**: `demo_matcher.py`  
**Purpose**: Test with multiple patient types

```bash
python demo_matcher.py
```

**What it does**:
- Tests 3 different patient profiles:
  - Non-Small Cell Lung Cancer
  - Type 2 Diabetes
  - Alzheimer's Disease
- Shows detailed results for each

**Output**: Detailed reports for each patient type

---

## Recommended Testing Order

1. **First**: Check if server is online
   ```bash
   python check_mcp_server.py
   ```

2. **If server is online**: Test endpoints
   ```bash
   python test_mcp_server.py
   ```

3. **If endpoints work**: Test full integration
   ```bash
   python test_mcp_integration.py
   ```

4. **If integration works**: Try the simple example
   ```bash
   python simple_example.py
   ```

5. **For full demo**: Run the demo script
   ```bash
   python demo_matcher.py
   ```

## Troubleshooting

### Server Returns 502
If you see "502 Bad Gateway":
1. Wait 30-60 seconds (cold start)
2. Check Render dashboard
3. Try again

### Import Errors
If you see import errors:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### No Output
If scripts run but show no output:
- Check that you're in the right directory
- Make sure virtual environment is activated
- Check that ANTHROPIC_API_KEY is set in .env

## Expected Output Examples

### When Server is Online:
```
[Step 1/4] Extracting medical conditions from patient data...
[Claude] Raw response: ["lung cancer", "stage IV"]
[Step 1/4] ✓ Extracted conditions: ['lung cancer', 'stage IV']

[Step 2/4] Searching ClinicalTrials.gov for: 'lung cancer stage IV'
[MCP] Calling tool 'list_studies'...
[MCP] Response status: 200
[Step 2/4] ✓ Found 15 trials: ['NCT12345678', 'NCT87654321', ...]
```

### When Server is Offline:
```
[MCP] Calling tool 'list_studies'...
[MCP] Response status: 502
[MCP] Server returned 502 Bad Gateway - server may be cold-starting or down
[Step 2/4] ✗ No result from MCP server
```

## Quick Commands Reference

```bash
# Activate virtual environment
source venv/bin/activate

# Quick server check
python check_mcp_server.py

# Test server endpoints
python test_mcp_server.py

# Test request formats
python test_mcp_detailed.py

# Full integration test
python test_mcp_integration.py

# Simple example
python simple_example.py

# Full demo
python demo_matcher.py
```

