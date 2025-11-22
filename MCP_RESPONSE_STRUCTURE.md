# MCP Server Response Structure Analysis

## Test Results Summary

✅ **MCP Server is WORKING** - All tests return 200 status codes

## Key Findings

### 1. Request Format (CORRECT)

The MCP server requires **JSON-RPC 2.0 format**:

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "list_studies",  // or "get_study"
    "arguments": {
      "cond": "breast cancer",
      "term": "",
      "locn": "",
      "overallStatus": "RECRUITING",
      "pageSize": 20,
      "format": "json",
      "countTotal": "true",
      "pageToken": ""
    }
  },
  "id": 1
}
```

**Required Headers:**
```
Content-Type: application/json
Accept: application/json, text/event-stream
```

**Endpoint:** Base URL only (`https://clinicaltrialsgov-mcp.onrender.com`)

---

### 2. Response Format (SSE - Server-Sent Events)

The server returns **Server-Sent Events (SSE)** format, not plain JSON:

```
event: message
data: {"result": {...}, "jsonrpc": "2.0", "id": 1}
```

**Must parse the `data:` line** to extract the JSON.

---

### 3. Response Structure

After parsing the SSE `data:` line, the structure is:

```json
{
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{...JSON string that needs to be parsed again...}"
      }
    ]
  },
  "jsonrpc": "2.0",
  "id": 1
}
```

**Key Point:** The actual data is in `result.content[0].text` as a **JSON string** that must be parsed again!

---

### 4. list_studies Response Structure

After parsing `result.content[0].text`:

```json
{
  "totalCount": 2463,
  "studies": [
    {
      "protocolSection": {
        "identificationModule": {
          "nctId": "NCT06807502",
          "briefTitle": "Evaluation of Circulating Tumor Cells...",
          "officialTitle": "...",
          "organization": {
            "fullName": "ScreenCell",
            "class": "INDUSTRY"
          }
        },
        "statusModule": {
          "overallStatus": "RECRUITING",
          ...
        }
      },
      "derivedSection": {...},
      "hasResults": false
    }
  ],
  "nextPageToken": "..."
}
```

**To extract NCT IDs:**
```python
parsed_data = json.loads(result["result"]["content"0]["text"])
nct_ids = [
    study["protocolSection"]["identificationModule"]["nctId"]
    for study in parsed_data["studies"]
]
```

---

### 5. get_study Response Structure

After parsing `result.content[0].text`:

```json
{
  "protocolSection": {
    "identificationModule": {
      "nctId": "NCT06807502",
      "briefTitle": "...",
      "officialTitle": "..."
    },
    "eligibilityModule": {
      "eligibilityCriteria": "INCLUSION CRITERIA\n\nFor all participants:\n* Age greater than or equal to 18 years\n...",
      "healthyVolunteers": "No",
      "sex": "All",
      "minimumAge": "18 Years",
      ...
    },
    "statusModule": {...},
    "descriptionModule": {
      "briefSummary": "...",
      "detailedDescription": "..."
    },
    ...
  }
}
```

**To extract eligibility criteria:**
```python
parsed_data = json.loads(result["result"]["content"][0]["text"])
eligibility = parsed_data["protocolSection"]["eligibilityModule"]["eligibilityCriteria"]
```

---

## What's Wrong in Current Code

### In `clinical_trial_matcher.py`:

1. ❌ **Wrong request format**: Using `{"arguments": {...}}` instead of JSON-RPC
2. ❌ **Wrong endpoint**: Trying `/mcp/tools/list_studies` instead of base URL
3. ❌ **Missing headers**: Not including `Accept: application/json, text/event-stream`
4. ❌ **Not parsing SSE**: Not handling Server-Sent Events format
5. ❌ **Wrong data extraction**: Not parsing `result.content[0].text` as JSON
6. ❌ **Wrong NCT ID path**: Looking for `studies[].nct_id` instead of `studies[].protocolSection.identificationModule.nctId`

---

## Correct Implementation Pattern

```python
# 1. Build JSON-RPC request
payload = {
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
        "name": "list_studies",
        "arguments": {
            "cond": "breast cancer",
            "term": "",
            "locn": "",
            "overallStatus": "RECRUITING",
            "pageSize": 20,
            "format": "json",
            "countTotal": "true",
            "pageToken": ""
        }
    },
    "id": 1
}

# 2. Send request with correct headers
response = requests.post(
    "https://clinicaltrialsgov-mcp.onrender.com",
    json=payload,
    headers={
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    },
    timeout=30
)

# 3. Parse SSE format
lines = response.text.strip().split('\n')
data_json = None
for line in lines:
    if line.startswith('data: '):
        data_json = line[6:]  # Remove "data: " prefix
        break

# 4. Parse JSON-RPC response
mcp_response = json.loads(data_json)

# 5. Extract and parse the actual data
text_data = mcp_response["result"]["content"][0]["text"]
parsed_data = json.loads(text_data)  # Parse JSON string

# 6. Extract NCT IDs
nct_ids = [
    study["protocolSection"]["identificationModule"]["nctId"]
    for study in parsed_data["studies"]
]
```

---

## Next Steps

1. ✅ Update `_call_mcp_tool()` to use JSON-RPC format
2. ✅ Add SSE parsing
3. ✅ Update `_search_trials_via_mcp()` to extract NCT IDs correctly
4. ✅ Update `_get_trial_details_via_mcp()` to parse response correctly
5. ✅ Extract eligibility criteria from the correct path

---

## Test Files Status

✅ `test_mcp_server.py` - Working correctly
✅ `test_mcp_detailed.py` - Working correctly (needs indentation fix)
✅ `test_mcp_structure.py` - Shows full structure analysis

All tests confirm the MCP server is functional and returning correct data!

