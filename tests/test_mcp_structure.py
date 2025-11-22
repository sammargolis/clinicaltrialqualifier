#!/usr/bin/env python3
"""
Test to understand the exact MCP response structure
"""

import requests
import json

MCP_SERVER_URL = "https://clinicaltrialsgov-mcp.onrender.com"

def test_list_studies_structure():
    """Test list_studies and show the full structure"""
    print("="*80)
    print("Testing list_studies - Full Response Structure")
    print("="*80)
    
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
                "pageSize": 3,  # Small number for testing
                "format": "json",
                "countTotal": "true",
                "pageToken": ""
            }
        },
        "id": 1
    }
    
    print(f"\nRequest payload:")
    print(json.dumps(payload, indent=2))
    
    try:
        response = requests.post(
            MCP_SERVER_URL,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            },
            timeout=30
        )
        
        print(f"\nStatus: {response.status_code}")
        
        if response.status_code == 200:
            # Parse SSE format
            lines = response.text.strip().split('\n')
            data_json = None
            
            for line in lines:
                if line.startswith('data: '):
                    data_json = line[6:]
                    break
            
            if data_json:
                mcp_response = json.loads(data_json)
                print(f"\n✓ MCP Response Structure:")
                print(f"  Type: {type(mcp_response)}")
                print(f"  Keys: {list(mcp_response.keys())}")
                
                # Extract the actual data
                if "result" in mcp_response:
                    result = mcp_response["result"]
                    print(f"\n  result keys: {list(result.keys())}")
                    
                    if "content" in result and len(result["content"]) > 0:
                        content = result["content"][0]
                        print(f"\n  content[0] keys: {list(content.keys())}")
                        print(f"  content[0] type: {content.get('type')}")
                        
                        # The actual data is in content[0].text as a JSON string
                        text_data = content.get("text", "")
                        print(f"\n  text length: {len(text_data)} characters")
                        print(f"  text preview (first 500 chars): {text_data[:500]}")
                        
                        # Parse the JSON string
                        try:
                            parsed_data = json.loads(text_data)
                            print(f"\n✓ Parsed text data structure:")
                            print(f"  Type: {type(parsed_data)}")
                            print(f"  Keys: {list(parsed_data.keys()) if isinstance(parsed_data, dict) else 'Not a dict'}")
                            
                            if isinstance(parsed_data, dict):
                                if "studies" in parsed_data:
                                    studies = parsed_data["studies"]
                                    print(f"\n  studies array length: {len(studies)}")
                                    if len(studies) > 0:
                                        print(f"\n  First study structure:")
                                        first_study = studies[0]
                                        print(f"    Type: {type(first_study)}")
                                        print(f"    Keys: {list(first_study.keys()) if isinstance(first_study, dict) else 'Not a dict'}")
                                        
                                        # Find NCT ID
                                        if isinstance(first_study, dict):
                                            protocol = first_study.get("protocolSection", {})
                                            ident = protocol.get("identificationModule", {})
                                            nct_id = ident.get("nctId")
                                            title = ident.get("briefTitle", "N/A")
                                            print(f"\n    NCT ID: {nct_id}")
                                            print(f"    Title: {title}")
                                            
                                            # Show how to extract NCT IDs
                                            print(f"\n✓ How to extract NCT IDs:")
                                            print(f"  parsed_data['studies'][i]['protocolSection']['identificationModule']['nctId']")
                                    
                                if "totalCount" in parsed_data:
                                    print(f"\n  totalCount: {parsed_data['totalCount']}")
                                    
                        except json.JSONDecodeError as e:
                            print(f"\n✗ Error parsing text as JSON: {e}")
                            print(f"  Text: {text_data[:200]}")
                            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

def test_get_study_structure():
    """Test get_study and show the full structure"""
    print("\n" + "="*80)
    print("Testing get_study - Full Response Structure")
    print("="*80)
    
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "get_study",
            "arguments": {
                "nct_id": "NCT06807502"  # Use a real NCT ID from the list_studies test
            }
        },
        "id": 1
    }
    
    print(f"\nRequest payload:")
    print(json.dumps(payload, indent=2))
    
    try:
        response = requests.post(
            MCP_SERVER_URL,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            },
            timeout=30
        )
        
        print(f"\nStatus: {response.status_code}")
        
        if response.status_code == 200:
            # Parse SSE format
            lines = response.text.strip().split('\n')
            data_json = None
            
            for line in lines:
                if line.startswith('data: '):
                    data_json = line[6:]
                    break
            
            if data_json:
                mcp_response = json.loads(data_json)
                print(f"\n✓ MCP Response Structure:")
                print(f"  Type: {type(mcp_response)}")
                print(f"  Keys: {list(mcp_response.keys())}")
                
                if "result" in mcp_response:
                    result = mcp_response["result"]
                    if "content" in result and len(result["content"]) > 0:
                        content = result["content"][0]
                        text_data = content.get("text", "")
                        
                        print(f"\n  text length: {len(text_data)} characters")
                        print(f"  text preview (first 1000 chars): {text_data[:1000]}")
                        
                        # Parse the JSON string
                        try:
                            parsed_data = json.loads(text_data)
                            print(f"\n✓ Parsed text data structure:")
                            print(f"  Type: {type(parsed_data)}")
                            
                            if isinstance(parsed_data, dict):
                                protocol = parsed_data.get("protocolSection", {})
                                ident = protocol.get("identificationModule", {})
                                nct_id = ident.get("nctId")
                                title = ident.get("briefTitle", "N/A")
                                
                                print(f"\n  NCT ID: {nct_id}")
                                print(f"  Title: {title}")
                                
                                # Show inclusion/exclusion criteria location
                                elig = protocol.get("eligibilityModule", {})
                                if elig:
                                    print(f"\n  Eligibility module found:")
                                    print(f"    Keys: {list(elig.keys())}")
                                    
                                    inclusion = elig.get("eligibilityCriteria", "")
                                    if inclusion:
                                        print(f"\n    Eligibility criteria length: {len(inclusion)} chars")
                                        print(f"    Preview: {inclusion[:300]}")
                                        
                        except json.JSONDecodeError as e:
                            print(f"\n✗ Error parsing text as JSON: {e}")
                            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run structure tests"""
    print("\n" + "="*80)
    print("MCP RESPONSE STRUCTURE ANALYSIS")
    print("="*80)
    
    test_list_studies_structure()
    test_get_study_structure()
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print("\nKey findings:")
    print("1. MCP returns SSE format: 'event: message\\ndata: {...}'")
    print("2. Parse the 'data:' line to get JSON")
    print("3. Response structure: result.content[0].text contains JSON string")
    print("4. For list_studies: Parse text to get {totalCount, studies[]}")
    print("5. NCT IDs are at: studies[i].protocolSection.identificationModule.nctId")
    print("6. For get_study: Parse text to get full trial details")
    print("7. Eligibility criteria at: protocolSection.eligibilityModule.eligibilityCriteria")

if __name__ == "__main__":
    main()

