#!/usr/bin/env python3
"""
Quick script to check if MCP server is online
Run this periodically to see when the server comes back up
"""

import requests
import sys

MCP_SERVER_URL = "https://clinicaltrialsgov-mcp.onrender.com"

def check_server():
    """Check if server is responding"""
    try:
        response = requests.get(MCP_SERVER_URL, timeout=10)
        
        if response.status_code == 200:
            print("✓ Server is ONLINE!")
            print(f"  Status: {response.status_code}")
            return True
        elif response.status_code == 502:
            print("✗ Server is OFFLINE (502 Bad Gateway)")
            print("  The server may be:")
            print("  - Cold-starting (wait 30-60 seconds)")
            print("  - Down or not deployed")
            print("  - Having issues")
            return False
        elif response.status_code == 406:
            print("✓ Server is ONLINE but returned 406 (Not Acceptable)")
            print("  This means the server is running but doesn't accept GET requests")
            print("  Try the full test scripts to find the correct endpoint format")
            return True  # Server is up, just needs correct format
        else:
            print(f"⚠ Server returned status: {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            return response.status_code < 500  # 4xx means server is up
            
    except requests.exceptions.Timeout:
        print("✗ Server request timed out")
        return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to server")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    print(f"Checking MCP server: {MCP_SERVER_URL}")
    print("-" * 60)
    
    is_online = check_server()
    
    if is_online:
        print("\n✓ Server is ready! You can now run:")
        print("  python test_mcp_integration.py")
        sys.exit(0)
    else:
        print("\n✗ Server is not ready. Try again in 30-60 seconds.")
        print("\nTo wake up the server:")
        print("  1. Visit https://dashboard.render.com")
        print("  2. Find the 'clinicaltrialsgov-mcp' service")
        print("  3. Click 'Manual Deploy' or wait for auto-wake")
        sys.exit(1)

