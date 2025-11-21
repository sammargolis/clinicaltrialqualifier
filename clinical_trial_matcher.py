"""
Clinical Trial Matcher using Claude AI Agent
This module uses Claude to intelligently match deidentified patient data
against clinical trial inclusion/exclusion criteria.
"""

import os
import re
from typing import List, Dict, Any, Optional
from anthropic import Anthropic
from pydantic import BaseModel
import json


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
    Uses advanced reasoning to evaluate complex medical criteria.
    """
    
    def __init__(self, api_key: Optional[str] = None, trials_file_path: str = "clinical_trials.txt"):
        """
        Initialize the Clinical Trial Matcher agent.
        
        Args:
            api_key: Anthropic API key (reads from ANTHROPIC_API_KEY env var if not provided)
            trials_file_path: Path to the clinical trials database file
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key must be provided or set in ANTHROPIC_API_KEY environment variable")
        
        self.client = Anthropic(api_key=self.api_key)
        self.trials_file_path = trials_file_path
        self.trials_database = self._load_trials()
    
    def _load_trials(self) -> str:
        """Load the clinical trials database from file"""
        try:
            with open(self.trials_file_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Clinical trials file not found at: {self.trials_file_path}")
    
    def _parse_trials(self, trials_text: str) -> List[Dict[str, Any]]:
        """Parse the clinical trials text into structured data"""
        trials = []
        
        # Try new format first (--- delimiter)
        if "\n---\n" in trials_text:
            trial_blocks = trials_text.split("\n---\n")
        else:
            # Fall back to old format (==== delimiter)
            trial_blocks = trials_text.split("=" * 80)
        
        for block in trial_blocks:
            if "TRIAL ID:" not in block:
                continue
            
            trial = {}
            
            # Extract basic info - works for both formats
            trial_id_match = re.search(r'TRIAL ID:\s*(\S+)', block, re.IGNORECASE)
            if trial_id_match:
                trial['trial_id'] = trial_id_match.group(1)
            
            # Try new format NAME: first
            name_match = re.search(r'NAME:\s*(.+?)(?:\n|$)', block, re.IGNORECASE)
            if not name_match:
                # Fall back to old format "Trial Name:"
                name_match = re.search(r'Trial Name:\s*(.+?)(?:\n|$)', block, re.IGNORECASE)
            if name_match:
                trial['trial_name'] = name_match.group(1).strip()
            
            contact_match = re.search(r'CONTACT:\s*(.+?)(?:\n|$)', block)
            if contact_match:
                trial['contact_info'] = contact_match.group(1).strip()
            
            # Extract full text for AI processing
            trial['full_text'] = block.strip()
            
            if trial.get('trial_id'):
                trials.append(trial)
        
        return trials
    
    def match_patient_to_trials(
        self, 
        deidentified_patient_data: str,
        max_trials_to_return: int = 10,
        progress_callback=None
    ) -> List[TrialMatch]:
        """
        Match a patient's deidentified data against all clinical trials.
        
        Args:
            deidentified_patient_data: The patient's medical information with PHI redacted
            max_trials_to_return: Maximum number of trials to return
            
        Returns:
            List of TrialMatch objects, sorted by confidence score (highest first)
        """
        # Parse trials
        trials = self._parse_trials(self.trials_database)
        
        # Create flexible system prompt for the agent
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
        for i, trial in enumerate(trials, 1):
            try:
                # Send progress update
                if progress_callback:
                    progress_callback(f"Evaluating trial {i}/{len(trials)}: {trial.get('trial_name', 'Unknown')}...")
                
                match_result = self._evaluate_single_trial(
                    deidentified_patient_data,
                    trial,
                    system_prompt
                )
                if match_result:
                    matches.append(match_result)
                else:
                    print(f"Warning: No match result returned for trial {trial.get('trial_id', 'unknown')}")
            except Exception as e:
                print(f"Error evaluating trial {trial.get('trial_id', 'unknown')}: {str(e)}")
                import traceback
                traceback.print_exc()
                continue
        
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
    Example usage of the Clinical Trial Matcher.
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
        # Initialize the matcher
        matcher = ClinicalTrialMatcher(trials_file_path="clinical_trials.txt")
        
        # Match patient to trials
        print("Evaluating patient against clinical trials database...")
        print("This may take a minute as we analyze each trial...\n")
        
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

