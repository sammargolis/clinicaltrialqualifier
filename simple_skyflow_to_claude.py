# simple_skyflow_to_claude.py

import requests
import json

# Your Skyflow-tokenized data (raw tokens visible)
skyflow_data = {
    "condition": "leukemia",
    "studies": [
        {
            "nct_id": "NCT12345",
            "title": "B-cell Acute Lymphoblastic Leukemia Study",
            
            # Skyflow tokens (as-is from your document)
            "patient_name": "[NAME_VGMgLRv]",
            "mrn": "[HEALTHCARE_NUMBER_tKNCgm6]",
            "dob": "[DOB_gCXQIV6]",
            "phone": "[PHONE_NUMBER_46UXbal]",
            "address": "[LOCATION_ADDRESS_STREET_S5USJli]",
            "emergency_contact": "[NAME_ldlMjxb]",
            "emergency_phone": "[PHONE_NUMBER_nwHLRg0]",
            "pcp": "[NAME_BuVLer5]",
            "attending": "[NAME_Jgf3GNQ]",
            
            # Clinical data (from your document)
            "age": 46,
            "sex": "Male",
            "race": "White",
            "insurance": "Aetna PPO",
            "visit_date": "2025-10-28",
            
            "chief_complaint": "Progressive fatigue, night sweats, lymphadenopathy, cytopenias consistent with relapsed B-cell acute lymphoblastic leukemia",
            
            "history": "46-year-old male with known history of B-cell ALL, originally diagnosed 2022. Initial CR with hyper-CVAD, consolidated with 2 cycles blinatumomab. Relapsed 2024 with 42% marrow blasts. Second-line inotuzumab ozogamicin yielded partial response, complicated by prolonged thrombocytopenia. Bone marrow biopsy 2025-09-18: 58% CD19+, CD22+ lymphoblasts. Cytogenetics: t(12;21)(p13;q22) and IKZF1 deletion. Mutations: NRAS G12D and TP53 R248Q (5% VAF). No CNS involvement. Current symptoms: drenching night sweats, exertional dyspnea, ecchymoses, low-grade fevers. ECOG PS 1.",
            
            "labs": {
                "hemoglobin": "7.4 g/dL",
                "hematocrit": "22.1%",
                "wbc": "2.8 K/uL",
                "anc": "710/uL",
                "platelets": "61 K/uL",
                "creatinine": "0.9 mg/dL",
                "ast": "38 U/L",
                "alt": "41 U/L",
                "bilirubin": "1.1 mg/dL",
                "lvef": "52%"
            },
            
            "imaging": "CT: Mild mediastinal/retroperitoneal lymphadenopathy (largest 2.1 cm). Mild splenomegaly. No pulmonary infiltrates.",
            
            "physical_exam": "BP 128/72, HR 96, RR 18, Temp 37.8C. Bilateral cervical/supraclavicular nodes up to 2.5 cm. Splenomegaly 3 cm below costal margin. Scattered ecchymoses on forearms."
        }
    ]
}

# Step 1: Load into API
print("Loading Skyflow-protected data...")
response = requests.post('http://localhost:8000/api/load', json=skyflow_data)
print(f"[OK] Loaded: {response.json()['message']}\n")

# Step 2: Claude reads and analyzes
print("Claude is reading the data...\n")

question = """Read this clinical case and provide:
1. Patient summary
2. Key risk factors
3. Treatment challenges
4. Clinical trial recommendations"""

response = requests.post(
    'http://localhost:8000/api/ask',
    json={"question": question}
)

result = response.json()

print("="*70)
print("CLAUDE'S ANALYSIS")
print("="*70)
print()
print(result['answer'])
print()
print("="*70)
print(f"Skyflow tokens protected: [NAME_VGMgLRv], [HEALTHCARE_NUMBER_tKNCgm6], etc.")
print("="*70)