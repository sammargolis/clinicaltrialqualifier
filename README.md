# Clinical Trial Qualifier

An intelligent system for matching patients to clinical trials while maintaining privacy and HIPAA compliance through automated PHI redaction and AI-powered qualification.

## Overview

This project automates the process of qualifying patients for clinical trials by:
1. Processing patient medical records (EHR data)
2. Protecting patient privacy through automated PHI redaction
3. Using AI agents to match patients with relevant clinical trials
4. Evaluating inclusion/exclusion criteria programmatically

## Workflow

### 1. Patient Record Upload
Upload PDF documents containing patient records (pseudo EHR data) for processing.

### 2. PHI Redaction with Skyflow Detect
Patient records are ingested using **Skyflow Detect** to automatically identify and redact Protected Health Information (PHI), creating a privacy-compliant redacted record.

### 3. Claude Agent Processing
The redacted patient record is passed to a **Claude AI agent** for intelligent analysis and matching.

### 4. Clinical Trial Retrieval
The agent queries the **Clinical Trials MCP (Model Context Protocol)** to retrieve potentially relevant clinical trials based on the patient's medical profile.

### 5. Qualification via Subagent
A specialized **subagent tool** evaluates the patient record against each trial's:
- Inclusion criteria
- Exclusion criteria

This determines which trials the patient qualifies for.

### 6. Optimization Loop
The agent evaluates whether the current set of trials is optimal or if additional MCP queries are needed to find better matches.

### 7. Results
Returns a curated set of qualified clinical trials that match the patient's profile and meet all eligibility criteria.

## Key Features

- **Privacy-First**: Automated PHI redaction ensures HIPAA compliance
- **Intelligent Matching**: Claude AI agents understand complex medical criteria
- **Iterative Optimization**: Agent can refine trial searches for optimal matches
- **Structured Evaluation**: Systematic assessment of inclusion/exclusion criteria

## Technologies

- **Skyflow Detect**: PHI detection and redaction
- **Claude AI (Sonnet 4)**: Intelligent agent orchestration and medical reasoning
- **Clinical Trials MCP Server**: Real-time access to ClinicalTrials.gov API v2 via Model Context Protocol
  - Repository: [ClinicalTrialsGov-MCP](https://github.com/caldavidlee/ClinicalTrialsGov-MCP)
  - Server: `https://clinicaltrialsgov-mcp.onrender.com`
- **Model Context Protocol (MCP)**: Standard for connecting AI agents to external data sources
- **ClinicalTrials.gov API v2**: Official API for accessing clinical trial data
- **FastAPI**: Modern, high-performance Python web framework
- **Uvicorn**: ASGI server for FastAPI
- **HTML/CSS/JavaScript**: User interface

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Anthropic API key (for Claude AI agent)
- Skyflow account (for PHI redaction)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd clinicaltrialqualifier
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
# Copy the example environment file
cp env.example .env

# Edit .env and add your API keys
nano .env
```

You'll need to add:
- `ANTHROPIC_API_KEY`: Get from https://console.anthropic.com/
- Skyflow credentials (already configured in app.py)

### Running the Application

**Option 1: Using the startup script (recommended)**
```bash
./run.sh
```

**Option 2: Using uvicorn directly**
```bash
source venv/bin/activate
uvicorn app:app --host 0.0.0.0 --port 5000 --reload
```

**Option 3: Using Python directly**
```bash
source venv/bin/activate
python app.py
```

Once running:
1. Open your browser and navigate to: `http://localhost:5000`
2. Enter medical information in the text box
3. Click "De-identify Information" to see PHI automatically redacted

**Bonus**: FastAPI provides interactive API documentation at:
- Swagger UI: `http://localhost:5000/docs`
- ReDoc: `http://localhost:5000/redoc`

### Example Usage

Try entering sample medical information like:
```
Patient John Smith, DOB 03/15/1975, SSN 123-45-6789, lives at 123 Main Street, Boston MA. 
Phone: 555-1234. Medical Record #: MRN-987654
```

The system will automatically detect and redact:
- Names
- Dates of birth
- Social Security Numbers
- Addresses
- Phone numbers
- Medical record numbers

## Use Cases

- Streamlining clinical trial recruitment
- Helping patients find suitable trials
- Reducing manual review time for trial coordinators
- Improving trial enrollment rates through better matching

## Claude Agent Implementation

### Overview

The system uses Claude Sonnet 4 as an intelligent agent to evaluate patient eligibility for clinical trials. The agent:

1. **Reads and understands** complex medical criteria from clinical trial protocols
2. **Analyzes** deidentified patient data against inclusion/exclusion criteria
3. **Reasons** about eligibility using medical knowledge
4. **Returns** structured results with confidence scores and detailed explanations

### Architecture

```
Patient Data → PHI Redaction (Skyflow) → Deidentified Data → Claude Agent → Trial Matches
                                                                    ↓
                                                          MCP Server
                                                                    ↓
                                                          ClinicalTrials.gov API
                                                          (Real-time data)
```

The system now uses an MCP (Model Context Protocol) server to access ClinicalTrials.gov in real-time:
- Extracts medical conditions from patient data using Claude
- Queries ClinicalTrials.gov through MCP `list_studies` tool
- Retrieves detailed trial information using MCP `get_study` tool
- Evaluates each trial's eligibility criteria against patient data

### Using the Clinical Trial Matcher

#### Option 1: Python Script (Direct)

```python
from clinical_trial_matcher import ClinicalTrialMatcher

# Initialize the matcher with MCP server
matcher = ClinicalTrialMatcher(
    mcp_server_url="https://clinicaltrialsgov-mcp.onrender.com"
)

# Your deidentified patient data
patient_data = """
Patient is a 62 year old with Stage IV NSCLC...
[deidentified medical information]
"""

# Match patient to trials (queries ClinicalTrials.gov in real-time)
matches = matcher.match_patient_to_trials(patient_data)

# Generate report
report = matcher.generate_report(matches)
print(report)
```

#### Option 2: FastAPI Endpoints

**Match trials only (with already deidentified data):**
```bash
curl -X POST http://localhost:5000/match_trials \
  -H "Content-Type: application/json" \
  -d '{
    "deidentified_text": "Patient is a 62 year old...",
    "max_trials": 10
  }'
```

**Complete workflow (de-identify + match):**
```bash
curl -X POST http://localhost:5000/deidentify_and_match \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Patient John Smith, DOB 03/15/1975..."
  }'
```

#### Option 3: Run Demo Script

```bash
# Activate virtual environment
source venv/bin/activate

# Run demo with example patients
python demo_matcher.py
```

The demo script includes three example patients:
- Non-Small Cell Lung Cancer patient
- Type 2 Diabetes with Cardiovascular Disease patient
- Alzheimer's Disease patient

Each will be evaluated against relevant clinical trials from ClinicalTrials.gov based on their medical conditions.

### Clinical Trials Data Source

The system now queries **ClinicalTrials.gov** in real-time through an MCP server, providing:

- **Live Data**: Access to over 400,000+ registered clinical trials
- **Up-to-Date Information**: Always current trial status, locations, and criteria
- **Comprehensive Coverage**: Trials across all medical conditions and phases
- **Intelligent Search**: Claude extracts conditions from patient data to find relevant trials

#### MCP Server Implementation

This project uses the **ClinicalTrialsGov-MCP** server, which provides a Model Context Protocol (MCP) interface to the ClinicalTrials.gov API v2. The MCP server is an open-source project that enables standardized access to clinical trial data.

**MCP Server Repository**: [https://github.com/caldavidlee/ClinicalTrialsGov-MCP](https://github.com/caldavidlee/ClinicalTrialsGov-MCP)

**About the MCP Server:**
- **Purpose**: ClinicalTrials.gov v2 MCP server with limited endpoints
- **Technology**: TypeScript-based MCP implementation
- **Deployment**: Available at `https://clinicaltrialsgov-mcp.onrender.com` (hosted on Render)
- **Protocol**: Implements Model Context Protocol (MCP) standard for AI agent integration

**MCP Server Tools:**
- `list_studies`: Searches ClinicalTrials.gov by medical condition
  - Parameters: `cond`, `term`, `locn`, `overallStatus`, `pageSize`, `format`, `countTotal`, `pageToken`
  - Returns: List of matching clinical trials with NCT IDs
- `get_study`: Retrieves detailed information for a specific trial by NCT ID
  - Parameters: `nct_id`
  - Returns: Complete trial details including eligibility criteria, description, and contact information

**Request Format:**
The MCP server uses JSON-RPC 2.0 format over HTTP with Server-Sent Events (SSE):
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "list_studies",
    "arguments": {
      "cond": "breast cancer",
      "pageSize": 20,
      "format": "json"
    }
  },
  "id": 1
}
```

**Response Format:**
The server returns SSE format with data in `result.content[0].text` as a JSON string that contains the actual ClinicalTrials.gov API response.

Each trial retrieved includes:
- Detailed inclusion/exclusion criteria
- Trial metadata (phase, status, sponsor, locations)
- Contact information for enrollment
- Study design and outcome measures

### How the Agent Works

The Claude agent uses a sophisticated multi-step evaluation process:

1. **Condition Extraction**: Analyzes patient data to identify primary medical conditions
2. **Trial Search**: Queries ClinicalTrials.gov via MCP `list_studies` tool
3. **Trial Retrieval**: Gets detailed information for each trial via MCP `get_study` tool
4. **Eligibility Evaluation**: Each trial is evaluated independently with:
   - Match status (QUALIFIED / NOT_QUALIFIED / NEEDS_MORE_INFO)
   - Confidence score (0.0 - 1.0)
   - Specific criteria met or not met
   - Detailed reasoning
5. **Ranking**: Results sorted by confidence score to prioritize best matches

### Example Output

```
================================================================================
CLINICAL TRIAL MATCHING REPORT
================================================================================

Total Trials Evaluated: 6
Qualified: 1
Not Qualified: 4
Needs More Information: 1

--------------------------------------------------------------------------------

1. Phase III Study of Novel Immunotherapy for Non-Small Cell Lung Cancer
   Trial ID: NCT05234567
   Status: QUALIFIED
   Confidence: 85.00%
   Contact: clinicaltrials@nci.gov | Phone: 1-800-555-0199

   ✓ Inclusion Criteria Met (9):
     • Age 18 years or older
     • Histologically confirmed NSCLC
     • Stage IIIB or IV disease
     • ECOG performance status 0-1
     • Prior platinum-based chemotherapy
     • PD-L1 expression ≥50%
     • Adequate organ function
     • Life expectancy ≥3 months
     • Willing to provide tissue sample

   ✗ Inclusion Criteria Not Met (0):

   ⚠ Exclusion Criteria Violated (0):

   Reasoning:
     The patient meets all major inclusion criteria for this immunotherapy trial.
     PD-L1 expression of 65% exceeds the 50% threshold.
     Laboratory values are within acceptable ranges.
     No exclusion criteria are violated based on available information.
```

### API Response Structure

```json
{
  "matches": [
    {
      "trial_id": "NCT05234567",
      "trial_name": "Phase III Study of Novel Immunotherapy...",
      "match_status": "QUALIFIED",
      "confidence_score": 0.85,
      "inclusion_criteria_met": ["Age 18 years or older", "..."],
      "inclusion_criteria_not_met": [],
      "exclusion_criteria_violated": [],
      "reasoning": "Detailed explanation...",
      "contact_info": "clinicaltrials@nci.gov | Phone: 1-800-555-0199"
    }
  ],
  "report": "Full formatted report text..."
}
```

## Customization

### Configuring the MCP Server

The default MCP server URL is `https://clinicaltrialsgov-mcp.onrender.com`. To use a different MCP server:

```python
matcher = ClinicalTrialMatcher(
    mcp_server_url="https://your-mcp-server.com"
)
```

### Using a Local MCP Server

To run your own MCP server locally for testing:

1. **Clone the ClinicalTrials.gov MCP repository**:
   ```bash
   git clone https://github.com/caldavidlee/ClinicalTrialsGov-MCP.git
   cd ClinicalTrialsGov-MCP
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Build the project**:
   ```bash
   npm run build
   ```

4. **Run the server**:
   ```bash
   npm run dev
   ```

5. **Update the URL** to point to your local server:

   ```python
   matcher = ClinicalTrialMatcher(
       mcp_server_url="http://localhost:3000"
   )
   ```

**MCP Server Source Code**: For more details about the MCP server implementation, see the [ClinicalTrialsGov-MCP GitHub repository](https://github.com/caldavidlee/ClinicalTrialsGov-MCP).

### Adjusting Agent Behavior

Modify `clinical_trial_matcher.py`:

- **Temperature**: Set to 0.3 for consistent yet flexible evaluation
- **Max Tokens**: Set to 2000 per trial evaluation. Increase for very detailed analysis
- **Model**: Uses `claude-sonnet-4-20250514` for best medical reasoning
- **Max Studies**: Default searches for up to 20 studies, returns top 10 matches
- **Search Strategy**: Modify `_extract_conditions_from_patient_data()` to adjust condition extraction

## Troubleshooting

### "ANTHROPIC_API_KEY not configured"
- Ensure you've created a `.env` file with your API key
- Check that `python-dotenv` is installed
- Verify the `.env` file is in the project root directory

### Agent takes too long
- The agent queries ClinicalTrials.gov and evaluates each trial sequentially
- Expect ~2-3 minutes for full workflow (search + 10 trial evaluations)
- Each MCP query takes ~2-5 seconds
- Each trial evaluation takes ~10-20 seconds

### Low confidence scores
- May indicate missing information in patient data
- Add more detailed medical history, lab values, and imaging results
- Ensure all relevant criteria are addressed in the patient data

### MCP connection errors
- Verify the MCP server URL is correct
- Check that https://clinicaltrialsgov-mcp.onrender.com is accessible
- Ensure network connectivity and no firewall blocking
- MCP server may be cold-starting (Render free tier) - retry after 30 seconds

---

*This project demonstrates the intersection of privacy-preserving technologies, AI agents, Model Context Protocol (MCP), and healthcare data to solve real-world clinical challenges.*

