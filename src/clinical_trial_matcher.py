"""
Clinical Trial Matcher using Claude AI Agent with MCP Integration
This module uses Claude to intelligently match deidentified patient data
against clinical trial inclusion/exclusion criteria by querying the
ClinicalTrials.gov API through an MCP server.
"""

import os
import re
from typing import List, Dict, Any, Optional
from anthropic import Anthropic
from pydantic import BaseModel
import json
import requests


class TrialMatch(BaseModel):
    """Represents a clinical trial match result"""
    trial_id: str
    trial_name: str
    match_status: str  # "QUALIFIED", "NOT_QUALIFIED", "NEEDS_MORE_INFO"
    confidence_score: float  # 0.0 to 1.0
    inclusion_criteria_met: List[str]
    inclusion_criteria_not_met: List[str]
    exclusion_criteria_violated: List[str]
    reasoning: str
    contact_info: str


class ClinicalTrialMatcher:
    """
    Claude-powered agent for matching patients to clinical trials.
    Uses advanced reasoning to evaluate complex medical criteria and
    queries ClinicalTrials.gov API through an MCP server.
    """
    
    def __init__(
        self, 
        api_key: Optional[str] = None, 
        mcp_server_url: str = "https://clinicaltrialsgov-mcp.onrender.com"
    ):
        """
        Initialize the Clinical Trial Matcher agent.
        
        Args:
            api_key: Anthropic API key (reads from ANTHROPIC_API_KEY env var if not provided)
            mcp_server_url: URL of the MCP server for ClinicalTrials.gov API access
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key must be provided or set in ANTHROPIC_API_KEY environment variable")
        
        self.client = Anthropic(api_key=self.api_key)
        self.mcp_server_url = mcp_server_url.rstrip('/')
    
    def _call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Call an MCP tool on the remote server using JSON-RPC 2.0 format.
        
        Args:
            tool_name: Name of the MCP tool (list_studies or get_study)
            arguments: Arguments to pass to the tool
            
        Returns:
            The parsed data from the tool response, or None if error
        """
        try:
            print(f"\n[MCP] Calling tool '{tool_name}' with arguments: {arguments}")
            print(f"[MCP] Server URL: {self.mcp_server_url}")
            
            # Build JSON-RPC 2.0 request
            payload = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                },
                "id": 1
            }
            
            # Use base URL - MCP server handles routing
            endpoint = self.mcp_server_url
            
            print(f"[MCP] Endpoint: {endpoint}")
            print(f"[MCP] Payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(
                endpoint,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream"
                },
                timeout=30
            )
            
            print(f"[MCP] Response status: {response.status_code}")
            
            if response.status_code == 200:
                # Server returns Server-Sent Events (SSE) format
                # Parse the SSE response: "event: message\ndata: {...}\n\n"
                lines = response.text.strip().split('\n')
                data_json = None
                
                for line in lines:
                    if line.startswith('data: '):
                        data_json = line[6:]  # Remove "data: " prefix
                        break
                
                if not data_json:
                    print(f"[MCP] ✗ Could not find 'data:' line in SSE response")
                    print(f"[MCP] Response text: {response.text[:500]}")
                    return None
                
                # Parse JSON-RPC response
                try:
                    mcp_response = json.loads(data_json)
                    print(f"[MCP] ✓ Parsed JSON-RPC response")
                    
                    # Extract the actual data from result.content[0].text
                    if "result" in mcp_response:
                        result = mcp_response["result"]
                        if "content" in result and len(result["content"]) > 0:
                            content = result["content"][0]
                            if "text" in content:
                                # The actual data is in text as a JSON string
                                text_data = content["text"]
                                print(f"[MCP] ✓ Extracted text data ({len(text_data)} chars)")
                                
                                # Parse the JSON string to get the actual data
                                try:
                                    parsed_data = json.loads(text_data)
                                    print(f"[MCP] ✓ Successfully parsed data")
                                    return parsed_data
                                except json.JSONDecodeError as e:
                                    print(f"[MCP] ✗ Error parsing text as JSON: {e}")
                                    print(f"[MCP] Text preview: {text_data[:200]}")
                                    return None
                            else:
                                print(f"[MCP] ✗ No 'text' field in content")
                                return None
                        else:
                            print(f"[MCP] ✗ No content in result")
                            return None
                    else:
                        print(f"[MCP] ✗ No 'result' in response")
                        print(f"[MCP] Response keys: {list(mcp_response.keys())}")
                        return None
                        
                except json.JSONDecodeError as e:
                    print(f"[MCP] ✗ Error parsing SSE data as JSON: {e}")
                    print(f"[MCP] Data: {data_json[:500]}")
                    return None
                    
            elif response.status_code == 502:
                print(f"[MCP] ✗ Server returned 502 Bad Gateway - server may be cold-starting or down")
                print(f"[MCP] Please wait 30-60 seconds and try again, or check server status")
                return None
            else:
                print(f"[MCP] ✗ Unexpected status: {response.status_code}")
                print(f"[MCP] Response: {response.text[:500]}")
                return None
                
        except requests.exceptions.Timeout:
            print(f"[MCP] ✗ Request timed out after 30 seconds")
            return None
        except requests.exceptions.ConnectionError as e:
            print(f"[MCP] ✗ Connection error: {str(e)}")
            return None
        except Exception as e:
            print(f"[MCP] ✗ Error calling tool {tool_name}: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def _extract_conditions_from_patient_data(self, patient_data: str) -> List[str]:
        """
        Use Claude to extract medical conditions from patient data for trial search.
        
        Args:
            patient_data: Deidentified patient information
            
        Returns:
            List of medical conditions/search terms
        """
        print("\n[Step 1/4] Extracting medical conditions from patient data...")
        
        prompt = f"""Analyze this patient's medical information and extract the PRIMARY medical condition(s) 
that should be used to search for clinical trials. Focus on the main diagnosis, disease type, and stage.

Patient Information:
{patient_data}

Return ONLY a JSON array of search terms, like: ["breast cancer", "stage IV", "HER2 positive"]

Be specific but also practical for clinical trial searches. Include:
- Primary disease/condition
- Disease stage or severity if mentioned
- Important biomarkers or subtypes

Return format: ["term1", "term2", "term3"]"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.content[0].text.strip()
            print(f"[Claude] Raw response: {response_text}")
            
            # Extract JSON array
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                conditions = json.loads(json_match.group(0))
                print(f"[Step 1/4] ✓ Extracted conditions: {conditions}")
                return conditions
            else:
                # Fallback: try to extract any quoted strings
                conditions = re.findall(r'"([^"]+)"', response_text)
                print(f"[Step 1/4] ✓ Extracted conditions (fallback): {conditions}")
                return conditions
                
        except Exception as e:
            print(f"[Step 1/4] ✗ Error extracting conditions: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def _search_trials_via_mcp(self, conditions: List[str], max_studies: int = 20) -> List[str]:
        """
        Search for clinical trials using the MCP list_studies tool.
        
        Args:
            conditions: List of medical conditions to search for
            max_studies: Maximum number of studies to return
            
        Returns:
            List of trial NCT IDs
        """
        # Combine conditions into a search query
        search_query = " ".join(conditions)
        
        print(f"\n[Step 2/4] Searching ClinicalTrials.gov for: '{search_query}'")
        print(f"[Step 2/4] Requesting up to {max_studies} studies...")
        
        # Build MCP arguments with all required fields
        mcp_arguments = {
            "cond": search_query,
            "term": "",  # Additional search term (optional)
            "locn": "",  # Location filter (optional)
            "overallStatus": "RECRUITING",  # Filter by status
            "pageSize": max_studies,
            "format": "json",
            "countTotal": "true",
            "pageToken": ""  # For pagination
        }
        
        # Call the MCP list_studies tool
        result = self._call_mcp_tool("list_studies", mcp_arguments)
        
        if not result:
            print(f"[Step 2/4] ✗ No result from MCP server")
            return []
        
        print(f"[Step 2/4] MCP response type: {type(result)}")
        
        # Result should be the parsed data from list_studies
        # Structure: {"totalCount": 2463, "studies": [...], "nextPageToken": "..."}
        if isinstance(result, dict):
            studies = result.get("studies", [])
            total_count = result.get("totalCount", 0)
            
            print(f"[Step 2/4] Found {total_count} total trials, processing {len(studies)} in this page")
            
            if isinstance(studies, list) and studies:
                # Extract NCT IDs from correct path
                nct_ids = []
                for study in studies:
                    if isinstance(study, dict):
                        protocol = study.get("protocolSection", {})
                        ident = protocol.get("identificationModule", {})
                        nct_id = ident.get("nctId")
                        if nct_id:
                            nct_ids.append(nct_id)
                
                if nct_ids:
                    print(f"[Step 2/4] ✓ Extracted {len(nct_ids)} NCT IDs: {nct_ids[:5]}{'...' if len(nct_ids) > 5 else ''}")
                    return nct_ids[:max_studies]
                else:
                    print(f"[Step 2/4] ✗ No NCT IDs found in studies")
                    print(f"[Step 2/4] First study keys: {list(studies[0].keys()) if studies else 'No studies'}")
            else:
                print(f"[Step 2/4] ✗ Studies is not a list or is empty")
        else:
            print(f"[Step 2/4] ✗ Result is not a dictionary")
            print(f"[Step 2/4] Result type: {type(result)}")
        
        print(f"[Step 2/4] ✗ Could not extract trial IDs from response")
        return []
    
    def _get_trial_details_via_mcp(self, nct_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed trial information using the MCP get_study tool.
        
        Args:
            nct_id: NCT ID of the trial
            
        Returns:
            Trial details as a dictionary
        """
        print(f"[Step 3/4] Retrieving details for trial {nct_id}...")
        
        # Call MCP with correct argument format
        result = self._call_mcp_tool("get_study", {"nct_id": nct_id})
        
        if not result:
            print(f"[Step 3/4] ✗ No result for {nct_id}")
            return None
        
        # Result should be the parsed protocolSection data
        # Structure: {"protocolSection": {...}, ...}
        trial = {
            "trial_id": nct_id,
            "trial_name": "Unknown",
            "contact_info": "Not available",
            "full_text": ""
        }
        
        # Extract information from the parsed response
        if isinstance(result, dict):
            protocol = result.get("protocolSection", {})
            
            if protocol:
                # Extract identification info
                ident = protocol.get("identificationModule", {})
                trial["trial_name"] = ident.get("briefTitle") or ident.get("officialTitle") or "Unknown"
                
                # Extract eligibility criteria and other details
                elig = protocol.get("eligibilityModule", {})
                description = protocol.get("descriptionModule", {})
                status = protocol.get("statusModule", {})
                
                # Build full text with all relevant information
                full_text_parts = []
                
                # Title
                if ident.get("briefTitle"):
                    full_text_parts.append(f"TRIAL ID: {nct_id}")
                    full_text_parts.append(f"NAME: {ident.get('briefTitle')}")
                    if ident.get("officialTitle") and ident.get("officialTitle") != ident.get("briefTitle"):
                        full_text_parts.append(f"OFFICIAL TITLE: {ident.get('officialTitle')}")
                
                # Status
                if status.get("overallStatus"):
                    full_text_parts.append(f"STATUS: {status.get('overallStatus')}")
                
                # Description
                if description.get("briefSummary"):
                    full_text_parts.append(f"\nBRIEF SUMMARY:\n{description.get('briefSummary')}")
                if description.get("detailedDescription"):
                    full_text_parts.append(f"\nDETAILED DESCRIPTION:\n{description.get('detailedDescription')}")
                
                # Eligibility criteria (most important for matching)
                if elig.get("eligibilityCriteria"):
                    full_text_parts.append(f"\nELIGIBILITY CRITERIA:\n{elig.get('eligibilityCriteria')}")
                
                # Additional eligibility info
                if elig.get("minimumAge"):
                    full_text_parts.append(f"MINIMUM AGE: {elig.get('minimumAge')}")
                if elig.get("sex"):
                    full_text_parts.append(f"SEX: {elig.get('sex')}")
                if elig.get("healthyVolunteers"):
                    full_text_parts.append(f"HEALTHY VOLUNTEERS: {elig.get('healthyVolunteers')}")
                
                # Contact information
                contacts = protocol.get("contactsLocationsModule", {})
                if contacts:
                    central_contacts = contacts.get("centralContact", [])
                    if central_contacts:
                        contact = central_contacts[0]
                        contact_info = []
                        if contact.get("name"):
                            contact_info.append(contact.get("name"))
                        if contact.get("phone"):
                            contact_info.append(f"Phone: {contact.get('phone')}")
                        if contact.get("email"):
                            contact_info.append(contact.get("email"))
                        if contact_info:
                            trial["contact_info"] = " | ".join(contact_info)
                
                trial["full_text"] = "\n".join(full_text_parts)
            else:
                # Fallback: use the whole result as text
                trial["full_text"] = json.dumps(result, indent=2)
        else:
            trial["full_text"] = str(result)
        
        print(f"[Step 3/4] ✓ Retrieved trial: {trial['trial_name'][:60]}...")
        return trial
    
    def match_patient_to_trials(
        self, 
        deidentified_patient_data: str,
        max_trials_to_return: int = 10,
        progress_callback=None
    ) -> List[TrialMatch]:
        """
        Match a patient's deidentified data against clinical trials from ClinicalTrials.gov.
        Uses the MCP server to search for and retrieve trial information.
        
        Args:
            deidentified_patient_data: The patient's medical information with PHI redacted
            max_trials_to_return: Maximum number of trials to return
            progress_callback: Optional callback function for progress updates
            
        Returns:
            List of TrialMatch objects, sorted by confidence score (highest first)
        """
        print("\n" + "="*80)
        print("CLINICAL TRIAL MATCHING WITH MCP")
        print("="*80)
        
        # Step 1: Extract medical conditions from patient data
        if progress_callback:
            progress_callback("[Step 1/4] Analyzing patient data to identify conditions...")
        
        conditions = self._extract_conditions_from_patient_data(deidentified_patient_data)
        
        if not conditions:
            print("[WARNING] Could not extract conditions from patient data")
            print("[WARNING] Using fallback search term")
            conditions = ["clinical trial"]  # Fallback
        else:
            print(f"\n[SUCCESS] Identified conditions: {', '.join(conditions)}")
        
        # Step 2: Search for relevant trials via MCP
        if progress_callback:
            progress_callback(f"[Step 2/4] Searching ClinicalTrials.gov for: {', '.join(conditions)}...")
        
        trial_ids = self._search_trials_via_mcp(conditions, max_studies=max_trials_to_return * 2)
        
        if not trial_ids:
            print("\n" + "="*80)
            print("[ERROR] No trials found matching the patient's conditions")
            print("="*80)
            print("\nThis usually means:")
            print("  1. MCP server is down (502 Bad Gateway)")
            print("  2. MCP server is cold-starting (wait 30-60 seconds)")
            print("  3. No matching trials exist for the conditions")
            print(f"\nMCP Server: {self.mcp_server_url}")
            print("\nTo fix:")
            print("  - Check Render dashboard: https://dashboard.render.com")
            print("  - Wake up the service by visiting the URL in a browser")
            print("  - Wait 30-60 seconds for cold start")
            print("  - Check server logs on Render")
            print("="*80)
            return []
        
        print(f"\n[SUCCESS] Found {len(trial_ids)} potential trials from ClinicalTrials.gov")
        
        # Step 3: Get detailed information for each trial and evaluate
        system_prompt = """You are an expert clinical trial coordinator helping match patients to potentially suitable trials. Your goal is to identify reasonable matches based on available information.

Approach:
1. Read through all the patient information provided (in any format)
2. Review the trial's key criteria (condition, stage, treatments, etc.)
3. Determine if this seems like a REASONABLE MATCH
4. Be FLEXIBLE - patient data may be incomplete or in various formats
5. Focus on the MAIN condition and major criteria, not every minor detail

Match Criteria:
- QUALIFIED: The patient's main condition and key characteristics match the trial. They seem like a good candidate even if some minor details are missing.
- NOT_QUALIFIED: Clear mismatch (wrong disease, violates major exclusion like having the wrong cancer type)
- NEEDS_MORE_INFO: Could be a match but critical information is missing

Be lenient and practical. Look for potential matches, not perfect matches."""

        matches = []
        
        # Evaluate each trial
        print(f"\n[Step 4/4] Evaluating {len(trial_ids)} trials for eligibility...")
        print("-"*80)
        
        for i, trial_id in enumerate(trial_ids, 1):
            try:
                # Send progress update
                print(f"\n[Trial {i}/{len(trial_ids)}] Processing {trial_id}")
                if progress_callback:
                    progress_callback(f"[Step 4/4] Evaluating trial {i}/{len(trial_ids)}: {trial_id}...")
                
                # Get trial details via MCP
                trial = self._get_trial_details_via_mcp(trial_id)
                
                if not trial:
                    print(f"[Trial {i}/{len(trial_ids)}] ✗ Could not retrieve details for {trial_id}")
                    continue
                
                print(f"[Trial {i}/{len(trial_ids)}] Evaluating: {trial['trial_name'][:60]}...")
                
                # Evaluate the trial
                match_result = self._evaluate_single_trial(
                    deidentified_patient_data,
                    trial,
                    system_prompt
                )
                
                if match_result:
                    matches.append(match_result)
                    print(f"[Trial {i}/{len(trial_ids)}] ✓ Result: {match_result.match_status} ({match_result.confidence_score:.0%} confidence)")
                else:
                    print(f"[Trial {i}/{len(trial_ids)}] ✗ No match result returned")
                    
            except Exception as e:
                print(f"[Trial {i}/{len(trial_ids)}] ✗ Error: {str(e)}")
                import traceback
                traceback.print_exc()
                continue
        
        print("\n" + "-"*80)
        
        # Sort by confidence score (highest first)
        matches.sort(key=lambda x: x.confidence_score, reverse=True)
        
        # Return top matches
        return matches[:max_trials_to_return]
    
    def _evaluate_single_trial(
        self,
        patient_data: str,
        trial: Dict[str, Any],
        system_prompt: str
    ) -> Optional[TrialMatch]:
        """
        Use Claude to evaluate a single trial against patient data.
        """
        
        # Create the evaluation prompt
        user_prompt = f"""Does this patient seem like a reasonable match for this clinical trial?

PATIENT INFORMATION:
{patient_data}

TRIAL:
{trial['full_text']}

Provide your evaluation in JSON format:
{{
    "match_status": "QUALIFIED" | "NOT_QUALIFIED" | "NEEDS_MORE_INFO",
    "confidence_score": <0.0 to 1.0>,
    "inclusion_criteria_met": [<main criteria that match>],
    "inclusion_criteria_not_met": [<important criteria that don't match>],
    "exclusion_criteria_violated": [<major exclusions violated>],
    "reasoning": "<brief explanation of why this is or isn't a match>"
}}

Guidelines:
- QUALIFIED: Main condition matches, key criteria align, seems like a good candidate
- NOT_QUALIFIED: Wrong disease/condition or violates a major exclusion
- NEEDS_MORE_INFO: Could work but need critical details
- Be flexible with data format and missing information
- Focus on major factors (disease type, stage, prior treatments) not minor details"""

        try:
            # Call Claude API
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                temperature=0.3,  # Slightly higher for flexible matching
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            # Extract the response text
            response_text = response.content[0].text
            
            # Parse JSON response
            # Handle markdown code blocks if present
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON object directly
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    raise ValueError("Could not find JSON in response")
            
            evaluation = json.loads(json_str)
            
            # Create TrialMatch object
            return TrialMatch(
                trial_id=trial['trial_id'],
                trial_name=trial['trial_name'],
                match_status=evaluation['match_status'],
                confidence_score=float(evaluation['confidence_score']),
                inclusion_criteria_met=evaluation['inclusion_criteria_met'],
                inclusion_criteria_not_met=evaluation['inclusion_criteria_not_met'],
                exclusion_criteria_violated=evaluation['exclusion_criteria_violated'],
                reasoning=evaluation['reasoning'],
                contact_info=trial.get('contact_info', 'Contact information not available')
            )
            
        except Exception as e:
            print(f"Error in Claude API call for trial {trial['trial_id']}: {str(e)}")
            return None
    
    def generate_report(self, matches: List[TrialMatch]) -> str:
        """
        Generate a human-readable report of trial matches.
        
        Args:
            matches: List of TrialMatch objects
            
        Returns:
            Formatted report string
        """
        if not matches:
            return "No clinical trials found matching the patient's profile."
        
        report = []
        report.append("=" * 80)
        report.append("CLINICAL TRIAL MATCHING REPORT")
        report.append("=" * 80)
        report.append(f"\nTotal Trials Evaluated: {len(matches)}")
        
        qualified = [m for m in matches if m.match_status == "QUALIFIED"]
        not_qualified = [m for m in matches if m.match_status == "NOT_QUALIFIED"]
        needs_info = [m for m in matches if m.match_status == "NEEDS_MORE_INFO"]
        
        report.append(f"Qualified: {len(qualified)}")
        report.append(f"Not Qualified: {len(not_qualified)}")
        report.append(f"Needs More Information: {len(needs_info)}")
        report.append("")
        
        # Detailed results
        for i, match in enumerate(matches, 1):
            report.append("-" * 80)
            report.append(f"\n{i}. {match.trial_name}")
            report.append(f"   Trial ID: {match.trial_id}")
            report.append(f"   Status: {match.match_status}")
            report.append(f"   Confidence: {match.confidence_score:.2%}")
            report.append(f"   Contact: {match.contact_info}")
            
            if match.inclusion_criteria_met:
                report.append(f"\n   ✓ Inclusion Criteria Met ({len(match.inclusion_criteria_met)}):")
                for criterion in match.inclusion_criteria_met:
                    report.append(f"     • {criterion}")
            
            if match.inclusion_criteria_not_met:
                report.append(f"\n   ✗ Inclusion Criteria Not Met ({len(match.inclusion_criteria_not_met)}):")
                for criterion in match.inclusion_criteria_not_met:
                    report.append(f"     • {criterion}")
            
            if match.exclusion_criteria_violated:
                report.append(f"\n   ⚠ Exclusion Criteria Violated ({len(match.exclusion_criteria_violated)}):")
                for criterion in match.exclusion_criteria_violated:
                    report.append(f"     • {criterion}")
            
            report.append(f"\n   Reasoning:")
            # Wrap reasoning text
            reasoning_lines = match.reasoning.split('. ')
            for line in reasoning_lines:
                if line:
                    report.append(f"     {line.strip()}.")
            
            report.append("")
        
        report.append("=" * 80)
        report.append("END OF REPORT")
        report.append("=" * 80)
        
        return "\n".join(report)


def main():
    """
    Example usage of the Clinical Trial Matcher with MCP server.
    """
    # Example deidentified patient data
    patient_data = """
    Patient is a [REDACTED_AGE] year old [REDACTED_GENDER] with recently diagnosed 
    Stage IV non-small cell lung cancer (adenocarcinoma). Biopsy confirmed on [REDACTED_DATE].
    
    PD-L1 expression: 65% by immunohistochemistry
    ECOG performance status: 1
    
    Prior treatment: Completed 4 cycles of carboplatin/pemetrexed chemotherapy 
    ending [REDACTED_DATE]. Partial response seen on imaging.
    
    Current medications: None for cancer currently
    
    Recent labs:
    - WBC: 6,200/μL
    - ANC: 3,100/μL
    - Platelets: 185,000/μL
    - Hemoglobin: 11.2 g/dL
    - Creatinine: 0.9 mg/dL
    - Total bilirubin: 0.8 mg/dL
    - AST: 28 U/L
    - ALT: 32 U/L
    
    Imaging: CT chest/abdomen/pelvis shows primary lung mass with mediastinal lymphadenopathy
    and small liver metastases. No brain metastases on MRI brain performed [REDACTED_DATE].
    
    Medical history:
    - Hypertension (well-controlled)
    - Hyperlipidemia
    
    No history of autoimmune disease, HIV, hepatitis B/C, or other malignancies.
    No active infections.
    Non-smoker for past 10 years (previously 20 pack-year history).
    """
    
    try:
        # Initialize the matcher with MCP server
        matcher = ClinicalTrialMatcher(
            mcp_server_url="https://clinicaltrialsgov-mcp.onrender.com"
        )
        
        # Match patient to trials
        print("Analyzing patient data and searching ClinicalTrials.gov...")
        print("This may take a minute as we query the API and analyze each trial...\n")
        
        matches = matcher.match_patient_to_trials(patient_data)
        
        # Generate and print report
        report = matcher.generate_report(matches)
        print(report)
        
        # Also save to file
        with open("trial_matching_report.txt", "w") as f:
            f.write(report)
        print("\nReport also saved to: trial_matching_report.txt")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

