#!/usr/bin/env python3
"""
Demo script for the Clinical Trial Matcher
This script demonstrates how to use the Claude-powered agent to match
deidentified patient data against clinical trials.
"""

import os
from dotenv import load_dotenv
from clinical_trial_matcher import ClinicalTrialMatcher

# Load environment variables
load_dotenv()

# Example deidentified patient data for different conditions

PATIENT_EXAMPLE_1_NSCLC = """
Patient is a 62 year old male with recently diagnosed Stage IV non-small cell 
lung cancer (adenocarcinoma). Biopsy confirmed on 2024-03-15.

PD-L1 expression: 65% by immunohistochemistry
ECOG performance status: 1

Prior treatment: Completed 4 cycles of carboplatin/pemetrexed chemotherapy 
ending 2024-10-20. Partial response seen on imaging.

Current medications: None for cancer currently

Recent labs (2024-11-15):
- WBC: 6,200/μL
- ANC: 3,100/μL
- Platelets: 185,000/μL
- Hemoglobin: 11.2 g/dL
- Creatinine: 0.9 mg/dL
- Total bilirubin: 0.8 mg/dL
- AST: 28 U/L
- ALT: 32 U/L

Imaging: CT chest/abdomen/pelvis shows primary lung mass with mediastinal 
lymphadenopathy and small liver metastases. MRI brain from 2024-11-10 shows 
no brain metastases.

Medical history:
- Hypertension (well-controlled on lisinopril)
- Hyperlipidemia (on atorvastatin)

No history of autoimmune disease, HIV, hepatitis B/C, or other malignancies.
No active infections.
Non-smoker for past 10 years (previously 20 pack-year history).
"""

PATIENT_EXAMPLE_2_DIABETES = """
Patient is a 58 year old female with type 2 diabetes mellitus diagnosed 8 years ago.

Current HbA1c: 8.2% (tested 2024-11-01)
BMI: 32 kg/m²

Cardiovascular history:
- Myocardial infarction in 2021, treated with PCI and stent placement
- Currently on aspirin, clopidogrel, metoprolol, lisinopril, atorvastatin
- Last echocardiogram (2024-09-15): LVEF 55%, no significant abnormalities

Diabetes medications:
- Metformin 1000mg twice daily (stable dose for 6 months)
- Glipizide 10mg daily

Recent labs (2024-11-05):
- Fasting glucose: 165 mg/dL
- eGFR: 72 mL/min/1.73m²
- Creatinine: 0.9 mg/dL
- Blood pressure: 135/82 mmHg

Medical history:
- Hypertension (well-controlled)
- Dyslipidemia
- No history of pancreatitis
- No thyroid disease
- No recent cardiovascular events in past 6 months

Willing to perform self-monitoring of blood glucose and self-administer 
subcutaneous injections.
"""

PATIENT_EXAMPLE_3_ALZHEIMERS = """
Patient is a 72 year old male presenting with progressive memory decline 
over past 2 years.

Cognitive assessment:
- MMSE score: 24/30 (tested 2024-10-20)
- CDR global score: 0.5 (very mild dementia)
- Notable deficits in short-term memory and word-finding

Biomarker studies:
- Amyloid PET scan (2024-09-15): Positive, consistent with Alzheimer's pathology
- Tau PET scan (2024-10-01): Positive, showing moderate tau burden in 
  temporal and parietal regions
- CSF analysis: Low Aβ42, elevated tau

Brain MRI (2024-09-20):
- Mild generalized atrophy
- No evidence of stroke or mass lesions
- Minimal white matter changes (Fazekas grade 1)
- No subdural hematoma or hydrocephalus

Current medications:
- Donepezil 10mg daily (started 6 months ago, well-tolerated)
- Lisinopril for hypertension
- Atorvastatin for hyperlipidemia

Medical history:
- Hypertension (controlled)
- Hyperlipidemia (controlled)
- No history of seizures, stroke, or other neurological disorders
- No history of major depression or psychiatric illness
- No head trauma

Labs (2024-11-01):
- Vitamin B12: Normal
- TSH: Normal
- eGFR: 68 mL/min/1.73m²
- AST: 24 U/L, ALT: 28 U/L

Spouse available as study partner, spends >20 hours per week with patient.
Patient is fluent in English, has adequate vision and hearing for testing.
No contraindications to MRI or PET scans.
"""


def run_demo(patient_data: str, patient_description: str):
    """Run the matcher on a sample patient"""
    print("=" * 80)
    print(f"DEMO: {patient_description}")
    print("=" * 80)
    print()
    
    try:
        # Check for API key
        if not os.environ.get("ANTHROPIC_API_KEY"):
            print("ERROR: ANTHROPIC_API_KEY not found in environment variables.")
            print("Please set it in your .env file or export it:")
            print("  export ANTHROPIC_API_KEY='your-api-key-here'")
            return
        
        # Initialize the matcher with MCP server
        print("Initializing Clinical Trial Matcher with MCP server...")
        matcher = ClinicalTrialMatcher(
            mcp_server_url="https://clinicaltrialsgov-mcp.onrender.com"
        )
        
        # Match patient to trials
        print(f"Evaluating {patient_description} against ClinicalTrials.gov...")
        print("This may take 1-2 minutes as we query the API and analyze each trial...\n")
        
        matches = matcher.match_patient_to_trials(patient_data, max_trials_to_return=10)
        
        # Generate and print report
        report = matcher.generate_report(matches)
        print(report)
        print()
        
        # Save individual report
        filename = f"trial_report_{patient_description.lower().replace(' ', '_')}.txt"
        with open(filename, "w") as f:
            f.write(report)
        print(f"Report saved to: {filename}\n")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()


def main():
    """Run demos for all example patients"""
    print("\n" + "=" * 80)
    print("CLINICAL TRIAL MATCHER - DEMONSTRATION")
    print("Using Claude AI and MCP to match patient data to ClinicalTrials.gov")
    print("=" * 80)
    print()
    
    demos = [
        (PATIENT_EXAMPLE_1_NSCLC, "NSCLC Patient"),
        (PATIENT_EXAMPLE_2_DIABETES, "Type 2 Diabetes Patient"),
        (PATIENT_EXAMPLE_3_ALZHEIMERS, "Alzheimer's Disease Patient"),
    ]
    
    for patient_data, description in demos:
        run_demo(patient_data, description)
        print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()

