#!/usr/bin/env python3
"""
Test script to check MCP server endpoints and response format
"""

import requests
import json

MCP_SERVER_URL = "https://clinicaltrialsgov-mcp.onrender.com"

def test_server_health():
    """Test if server is accessible"""
    print("="*80)
    print("TEST 1: Server Health Check")
    print("="*80)
    
    try:
        response = requests.get(MCP_SERVER_URL, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Response (first 500 chars): {response.text[:500]}")
        
        if response.status_code == 502:
            print("\n⚠️  Server returned 502 Bad Gateway")
            print("   This usually means:")
            print("   - Server is cold-starting (wait 30-60 seconds)")
            print("   - Server is down or not deployed")
            print("   - Server needs to be woken up")
        
        return response.status_code == 200
    except requests.exceptions.Timeout:
        print("✗ Request timed out")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"✗ Connection error: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_endpoint_patterns():
    """Test different endpoint patterns"""
    print("\n" + "="*80)
    print("TEST 2: Testing Endpoint Patterns")
    print("="*80)
    
    endpoints_to_test = [
        "/",
        "/mcp",
        "/mcp/tools",
        "/mcp/tools/list_studies",
        "/tools/list_studies",
        "/list_studies",
        "/api/tools/list_studies",
        "/v1/tools/list_studies",
    ]
    
    for endpoint in endpoints_to_test:
        url = f"{MCP_SERVER_URL}{endpoint}"
        print(f"\nTesting: {url}")
        try:
            # Try GET first
            response = requests.get(url, timeout=5)
            print(f"  GET {response.status_code}: {response.text[:100]}")
            
            # Try POST with JSON
            response = requests.post(
                url,
                json={"cond": "breast cancer", "max": 5},
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            print(f"  POST {response.status_code}: {response.text[:200]}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"  ✓ Valid JSON response!")
                    print(f"  Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                    return url, data
                except:
                    print(f"  Response is not JSON")
            
        except requests.exceptions.Timeout:
            print(f"  ✗ Timeout")
        except Exception as e:
            print(f"  ✗ Error: {str(e)[:100]}")
    
    return None, None

def test_list_studies():
    """Test the list_studies tool with correct JSON-RPC format"""
    print("\n" + "="*80)
    print("TEST 3: Testing list_studies Tool (JSON-RPC Format)")
    print("="*80)
    
    # Use base URL - MCP server handles routing
    endpoint = MCP_SERVER_URL
    
    # Correct JSON-RPC format with all required arguments
    test_arguments = {
        "cond": "breast cancer",
        "term": "",  # Additional search term
        "locn": "",  # Location filter
        "overallStatus": "RECRUITING",  # Status filter
        "pageSize": 5,
        "format": "json",
        "countTotal": "true",
        "pageToken": ""  # For pagination
    }
    
    # JSON-RPC payload format
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "list_studies",
            "arguments": test_arguments
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
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
                # Server returns Server-Sent Events (SSE) format
                # Parse the SSE response
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
                        print(f"✓ Success! Response type: {type(data)}")
                        print(f"Response structure:")
                        print(json.dumps(data, indent=2)[:2000])
                        return endpoint, data
                    else:
                        print(f"✗ Could not find 'data:' line in SSE response")
                        print(f"Response text: {response.text[:500]}")
                except json.JSONDecodeError as e:
                    print(f"✗ JSON decode error: {e}")
                    print(f"Response text: {response.text[:500]}")
                except Exception as e:
                    print(f"✗ Error parsing response: {e}")
                    print(f"Response text: {response.text[:500]}")
        else:
            print(f"✗ Status {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
    except requests.exceptions.Timeout:
        print(f"✗ Request timed out")
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return None, None

def test_get_study():
    """Test the get_study tool with correct JSON-RPC format"""
    print("\n" + "="*80)
    print("TEST 4: Testing get_study Tool (JSON-RPC Format)")
    print("="*80)
    
    # Use a known NCT ID
    nct_id = "NCT00001234"
    
    # Use base URL - MCP server handles routing
    endpoint = MCP_SERVER_URL
    
    # Correct JSON-RPC format
    test_arguments = {
        "nct_id": nct_id
    }
    
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "get_study",
            "arguments": test_arguments
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
                # Parse the SSE response
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
                        print(f"✓ Success! Response type: {type(data)}")
                        print(f"Response structure:")
                        print(json.dumps(data, indent=2)[:2000])
                        return endpoint, data
                    else:
                        print(f"✗ Could not find 'data:' line in SSE response")
                        print(f"Response text: {response.text[:500]}")
                except json.JSONDecodeError as e:
                    print(f"✗ JSON decode error: {e}")
                    print(f"Response text: {response.text[:500]}")
                except Exception as e:
                    print(f"✗ Error parsing response: {e}")
                    print(f"Response text: {response.text[:500]}")
        else:
            print(f"✗ Status {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
    except requests.exceptions.Timeout:
        print(f"✗ Request timed out")
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return None, None

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("MCP SERVER TESTING")
    print(f"Server URL: {MCP_SERVER_URL}")
    print("="*80)
    
    # Test 1: Health check (informational only - server may require POST)
    is_healthy = test_server_health()
    
    if not is_healthy:
        print("\n⚠️  Health check failed (expected - server requires POST requests)")
        print("   Continuing with tool tests...")
    
    # Test 2: Endpoint patterns
    working_endpoint, _ = test_endpoint_patterns()
    
    # Test 3: list_studies
    list_endpoint, list_data = test_list_studies()
    
    # Test 4: get_study
    get_endpoint, get_data = test_get_study()
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    if list_endpoint:
        print(f"✓ list_studies endpoint: {list_endpoint}")
        print(f"  Response structure: {type(list_data)}")
    else:
        print("✗ list_studies: No working endpoint found")
    
    if get_endpoint:
        print(f"✓ get_study endpoint: {get_endpoint}")
        print(f"  Response structure: {type(get_data)}")
    else:
        print("✗ get_study: No working endpoint found")
    
    if list_endpoint and get_endpoint:
        print("\n✓ MCP server is working!")
        print(f"\nUpdate clinical_trial_matcher.py to use:")
        print(f"  list_studies: {list_endpoint}")
        print(f"  get_study: {get_endpoint}")
    else:
        print("\n⚠️  MCP server endpoints not found or not working")
        print("   Check the server documentation or contact the server maintainer")

if __name__ == "__main__":
    main()

