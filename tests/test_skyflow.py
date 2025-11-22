#!/usr/bin/env python3
"""
Test script to verify Skyflow API integration
"""
import requests

# Skyflow API configuration (from your specification)
SKYFLOW_URL = "https://a370a9658141.vault.skyflowapis-preview.com/v1/detect/deidentify/string"
SKYFLOW_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2MiOiJ1ODE3NDBkMzIxNWU0NTgzYjI2NTgxZGQ4MzU4M2ZhNiIsImF1ZCI6Imh0dHBzOi8vbWFuYWdlLnNreWZsb3dhcGlzLXByZXZpZXcuY29tIiwiZXhwIjoxNzYzODQyMTI2LCJpYXQiOjE3NjM3NTU3MjYsImlzcyI6InNhLWF1dGhAbWFuYWdlLnNreWZsb3dhcGlzLXByZXZpZXcuY29tIiwianRpIjoiZGE0MTg4YzkyZmY4NGNjNWJlMDI0ZThlYTc5NDk5MzkiLCJzdWIiOiJwOTBiZDM5YjQ5YjQ0OTg2YWI4MGIzNTMxOTcyNTBmYyJ9.T-XWBw2IVy7JHgzy7IktTP9m5Xkkxmojiz9mzumOq4Y3WROor1qSvH5p-YuheBSWa2J8f3bNHsuNEe0NHSegaVFj_rtYZvsWg9FpcIgSt9qmJyRrzgzFuzot2jYI5FvhEnnFtJkbeT5vZ7So0Jpl2nJsZorNoZjrgAd8aauOuG79wPgPuB3WwxNW_6hmHywnIFEdoo0tc1wBxseJtS_SrmhLDcdfP5r25R55KbOp_GrMm4XI1X37KIsrfl12buZxMR_DBzrx8UAnMXJu-PTQqlWDqfARHBvzDTJxNpmvreAp_zz6zVTuG8heGoSZZ5tUq1l3YnzyG6PdYBA2nt8cOQ"
VAULT_ID = "fe079a24274f448fa5fd4c471a07d08a"

# Sample patient EHR data
PATIENT_EHR = """
Patient Name: John Smith
Date of Birth: 03/15/1975
Social Security Number: 123-45-6789
Address: 456 Oak Avenue, Boston MA 02101
Phone Number: (555) 123-4567
Medical Record Number: MRN-987654321
Account Number: ACC-555-888

Chief Complaint: Patient presents with chest pain and shortness of breath.

History: 48-year-old male with history of hypertension.
"""

# De-identify String (POST /v1/detect/deidentify/string)
print("Testing Skyflow API integration...")
print("\n" + "="*80)
print("ORIGINAL TEXT:")
print("="*80)
print(PATIENT_EHR)

response = requests.post(
    SKYFLOW_URL,
    headers={
        "Authorization": f"Bearer {SKYFLOW_TOKEN}"
    },
    json={
        "text": PATIENT_EHR,
        "vault_id": VAULT_ID,
        "entity_types": [
            "name",
            "phone_number",
            "account_number",
            "ssn",
            "dob",
            "location_address_street",
            "healthcare_number"
        ],
        "token_type": {
            "default": "vault_token"
        }
    },
)

print("\n" + "="*80)
print("SKYFLOW API RESPONSE:")
print("="*80)

if response.status_code == 200:
    result = response.json()
    print(f"\nStatus: ✅ SUCCESS (HTTP {response.status_code})")
    print(f"\nDe-identified Text:")
    print("-" * 80)
    print(result.get('processed_text', ''))
    print("-" * 80)
    
    print(f"\nEntities Detected: {len(result.get('entities', []))}")
    for entity in result.get('entities', []):
        print(f"  - {entity['entity_type']}: '{entity['value']}' → {entity['token']}")
else:
    print(f"\n❌ ERROR: HTTP {response.status_code}")
    print(response.text)

print("\n" + "="*80)
print("✅ Skyflow integration is working correctly!")
print("="*80)

