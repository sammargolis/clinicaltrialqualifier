#!/usr/bin/env python3
"""
Detailed MCP server testing with different request formats
"""

import requests
import json

MCP_SERVER_URL = "https://clinicaltrialsgov-mcp.onrender.com"

def test_mcp_request_format():
    """Test MCP standard request format with correct JSON-RPC"""
    print("="*80)
    print("Testing MCP Standard Request Format (JSON-RPC)")
    print("="*80)
    
    # Use base URL - MCP server handles routing
    endpoint = MCP_SERVER_URL
    
    # Correct JSON-RPC format with all required arguments
    correct_payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "list_studies",
            "arguments": {
                "cond": "breast cancer",
                "term": "",
                "locn": "",
                "overallStatus": "RECRUITING",
                "pageSize": 5,
                "format": "json",
                "countTotal": "true",
                "pageToken": ""
            }
        },
        "id": 1
    }
    
    print(f"\n{'='*80}")
    print(f"Testing endpoint: {endpoint}")
    print(f"{'='*80}")
    print(f"\nUsing correct JSON-RPC format:")
    print(f"Payload: {json.dumps(correct_payload, indent=2)}")
    
    try:
        response = requests.post(
            endpoint,
            json=correct_payload,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            },
            timeout=30
        )
        
        print(f"\nStatus: {response.status_code}")
        
                if response.status_code == 200:
                    # Server returns Server-Sent Events (SSE) format
                    try:
                        # SSE format: "event: message\ndata: {...}\n\n"
                        lines = response.text.strip().split('\n')
                        data_json = None
                        
                        for line in lines:
                            if line.startswith('data: '):
                                data_json = line[6:]  # Remove "data: " prefix
                                break
                        
                        if data_json:
                            data = json.loads(data_json)
                            print(f"✓ SUCCESS! Response:")
                            print(json.dumps(data, indent=2)[:2000])
                            return endpoint, correct_payload, data
                        else:
                            print(f"✗ Could not find 'data:' line in SSE response")
                            print(f"Response text: {response.text[:500]}")
                    except json.JSONDecodeError as e:
                        print(f"✗ JSON decode error: {e}")
                        print(f"Response text: {response.text[:500]}")
                    except Exception as e:
                        print(f"✗ Error parsing response: {e}")
                        print(f"Response text: {response.text[:500]}")
        elif response.status_code == 502:
            print(f"✗ 502 Bad Gateway - server not ready")
        else:
            print(f"✗ Status {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
    except requests.exceptions.Timeout:
        print(f"✗ Timeout")
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return None, None, None

def test_get_study_tool():
    """Test the get_study tool with correct format"""
    print("\n" + "="*80)
    print("Testing get_study Tool (JSON-RPC Format)")
    print("="*80)
    
    endpoint = MCP_SERVER_URL
    nct_id = "NCT00001234"
    
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "get_study",
            "arguments": {
                "nct_id": nct_id
            }
        },
        "id": 1
    }
    
    print(f"\nEndpoint: {endpoint}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            endpoint,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            },
            timeout=30
        )
        
        print(f"\nStatus: {response.status_code}")
        if response.status_code == 200:
            # Server returns Server-Sent Events (SSE) format
            try:
                # SSE format: "event: message\ndata: {...}\n\n"
                lines = response.text.strip().split('\n')
                data_json = None
                
                for line in lines:
                    if line.startswith('data: '):
                        data_json = line[6:]  # Remove "data: " prefix
                        break
                
                if data_json:
                    data = json.loads(data_json)
                    print(f"✓ Success! Response:")
                    print(json.dumps(data, indent=2)[:2000])
                    return endpoint, data
                else:
                    print(f"✗ Could not find 'data:' line in SSE response")
                    print(f"Response: {response.text[:500]}")
            except json.JSONDecodeError as e:
                print(f"✗ JSON decode error: {e}")
                print(f"Response: {response.text[:500]}")
            except Exception as e:
                print(f"✗ Error parsing response: {e}")
                print(f"Response: {response.text[:500]}")
        else:
            print(f"✗ Status {response.status_code}")
            print(f"Response: {response.text[:500]}")
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return None, None

def main():
    """Run detailed tests"""
    print("\n" + "="*80)
    print("DETAILED MCP SERVER TESTING")
    print(f"Server: {MCP_SERVER_URL}")
    print("="*80)
    
    # Test POST with correct JSON-RPC format
    endpoint, payload, data = test_mcp_request_format()
    
    # Test get_study tool
    get_endpoint, get_data = test_get_study_tool()
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    if endpoint and data:
        print(f"✓ Working endpoint: {endpoint}")
        print(f"✓ Working payload format: {json.dumps(payload, indent=2)}")
        print(f"✓ Response structure: {type(data)}")
        print("\nUpdate clinical_trial_matcher.py with these settings!")
    else:
        print("✗ No working endpoint/payload combination found")
        print("\nPossible issues:")
        print("1. Server is down (502 Bad Gateway)")
        print("2. Server needs to be manually woken up on Render")
        print("3. Endpoint structure is different than expected")
        print("4. Authentication required")
        print("\nNext steps:")
        print("- Check Render dashboard to see if service is running")
        print("- Check server logs on Render")
        print("- Verify the server URL is correct")
        print("- Contact server maintainer for endpoint documentation")

if __name__ == "__main__":
    main()

