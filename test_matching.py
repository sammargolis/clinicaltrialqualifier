#!/usr/bin/env python3
"""Quick test to verify the matching is working"""

import os
from dotenv import load_dotenv
from clinical_trial_matcher import ClinicalTrialMatcher

load_dotenv()

# NSCLC patient that should match the immunotherapy trial
patient = """
62 year old male with Stage IV non-small cell lung cancer (adenocarcinoma).
Diagnosis confirmed by biopsy 6 months ago.

PD-L1 expression: 65% by immunohistochemistry
ECOG performance status: 1
Measurable disease present on CT scan

Prior treatment: Completed 4 cycles of carboplatin/pemetrexed chemotherapy 
3 months ago with partial response.

Recent labs (2 weeks ago):
- ANC: 2,100/μL
- Platelets: 150,000/μL  
- Hemoglobin: 10.5 g/dL
- Creatinine: 0.9 mg/dL (CrCl 75 mL/min)
- Total bilirubin: 0.7 mg/dL
- AST: 25 U/L
- ALT: 30 U/L

Imaging: MRI brain 1 month ago showed no brain metastases.
CT chest/abdomen shows lung mass and liver lesions (Stage IV).

Medical history:
- Hypertension (controlled)
- No autoimmune disease
- No HIV, hepatitis B or C
- No active infections
- No other malignancies in past 5 years

Life expectancy estimated > 6 months.
Willing to provide tissue samples for biomarker testing.
"""

print("Testing Clinical Trial Matcher...")
print("=" * 70)

matcher = ClinicalTrialMatcher(trials_file_path="clinical_trials.txt")
matches = matcher.match_patient_to_trials(patient)

# Show summary
qualified = [m for m in matches if m.match_status == "QUALIFIED"]
not_qualified = [m for m in matches if m.match_status == "NOT_QUALIFIED"]
needs_info = [m for m in matches if m.match_status == "NEEDS_MORE_INFO"]

print(f"\n✅ Evaluation Complete!")
print(f"   Total trials evaluated: {len(matches)}")
print(f"   Qualified: {len(qualified)}")
print(f"   Not Qualified: {len(not_qualified)}")  
print(f"   Needs More Info: {len(needs_info)}")
print()

# Show qualified trials
if qualified:
    print("🎯 QUALIFIED TRIALS:")
    print("=" * 70)
    for match in qualified:
        print(f"\n✓ {match.trial_name}")
        print(f"  Trial ID: {match.trial_id}")
        print(f"  Confidence: {match.confidence_score:.0%}")
        print(f"  Contact: {match.contact_info}")
        print(f"\n  Reasoning: {match.reasoning[:200]}...")
else:
    print("⚠️  No qualified trials found.")

# Show trials that need more info
if needs_info:
    print("\n\n📋 TRIALS NEEDING MORE INFORMATION:")
    print("=" * 70)
    for match in needs_info:
        print(f"\n• {match.trial_name}")
        print(f"  Confidence: {match.confidence_score:.0%}")

# Generate full report
print("\n\n" + "=" * 70)
print("Generating detailed report...")
report = matcher.generate_report(matches)

# Save to file
with open("test_matching_report.txt", "w") as f:
    f.write(report)

print("✅ Full report saved to: test_matching_report.txt")
print("\nTest completed successfully! 🎉")

