#!/usr/bin/env python3
"""
Setup verification script for Clinical Trial Matcher
This script checks that all dependencies and configurations are correct.
"""

import sys
import os
from pathlib import Path


def check_python_version():
    """Check Python version"""
    print("✓ Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"  ✓ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"  ✗ Python {version.major}.{version.minor}.{version.micro} (Need 3.8+)")
        return False


def check_dependencies():
    """Check required packages"""
    print("\n✓ Checking dependencies...")
    required = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("requests", "Requests"),
        ("pydantic", "Pydantic"),
        ("anthropic", "Anthropic SDK"),
        ("dotenv", "python-dotenv"),
    ]
    
    all_ok = True
    for module_name, display_name in required:
        try:
            __import__(module_name)
            print(f"  ✓ {display_name}")
        except ImportError:
            print(f"  ✗ {display_name} (not installed)")
            all_ok = False
    
    return all_ok


def check_files():
    """Check required files exist"""
    print("\n✓ Checking required files...")
    required_files = [
        "app.py",
        "clinical_trial_matcher.py",
        "clinical_trials.txt",
        "demo_matcher.py",
        "requirements.txt",
        "env.example",
    ]
    
    all_ok = True
    for filename in required_files:
        if Path(filename).exists():
            print(f"  ✓ {filename}")
        else:
            print(f"  ✗ {filename} (missing)")
            all_ok = False
    
    return all_ok


def check_env_file():
    """Check .env file and API keys"""
    print("\n✓ Checking environment configuration...")
    
    if not Path(".env").exists():
        print("  ⚠ .env file not found")
        print("    Create one by copying env.example:")
        print("    cp env.example .env")
        return False
    
    print("  ✓ .env file exists")
    
    # Load and check for required keys
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        print("  ⚠ ANTHROPIC_API_KEY not configured")
        print("    Get your API key from: https://console.anthropic.com/")
        print("    Add it to your .env file")
        return False
    
    print("  ✓ ANTHROPIC_API_KEY is configured")
    return True


def test_anthropic_connection():
    """Test connection to Anthropic API"""
    print("\n✓ Testing Anthropic API connection...")
    
    try:
        from anthropic import Anthropic
        from dotenv import load_dotenv
        
        load_dotenv()
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        
        if not api_key or api_key == "your_api_key_here":
            print("  ⚠ Skipping API test (no valid API key)")
            return False
        
        client = Anthropic(api_key=api_key)
        
        # Make a simple test call
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=50,
            messages=[
                {"role": "user", "content": "Say 'API test successful' and nothing else."}
            ]
        )
        
        if response.content[0].text:
            print("  ✓ Successfully connected to Anthropic API")
            print(f"    Response: {response.content[0].text}")
            return True
        else:
            print("  ✗ Unexpected API response")
            return False
            
    except Exception as e:
        print(f"  ✗ Error connecting to API: {str(e)}")
        return False


def test_matcher_import():
    """Test importing the clinical trial matcher"""
    print("\n✓ Testing Clinical Trial Matcher import...")
    
    try:
        from clinical_trial_matcher import ClinicalTrialMatcher, TrialMatch
        print("  ✓ Successfully imported ClinicalTrialMatcher")
        return True
    except Exception as e:
        print(f"  ✗ Error importing: {str(e)}")
        return False


def main():
    """Run all checks"""
    print("=" * 70)
    print("CLINICAL TRIAL MATCHER - SETUP VERIFICATION")
    print("=" * 70)
    print()
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Required Files", check_files),
        ("Environment Config", check_env_file),
        ("Matcher Import", test_matcher_import),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"  ✗ Error in {name}: {str(e)}")
            results.append((name, False))
    
    # Optional API test (only if env is configured)
    if results[3][1]:  # If env config passed
        try:
            api_result = test_anthropic_connection()
            results.append(("API Connection", api_result))
        except:
            pass
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print()
    print(f"Checks passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All checks passed! You're ready to use the Clinical Trial Matcher.")
        print("\nNext steps:")
        print("  1. Run the demo: python demo_matcher.py")
        print("  2. Start the API server: ./run.sh or python app.py")
        print("  3. Visit http://localhost:5000/docs for API documentation")
    else:
        print("\n⚠ Some checks failed. Please address the issues above.")
        if not results[3][1]:  # env config failed
            print("\nQuick fix:")
            print("  1. cp env.example .env")
            print("  2. Edit .env and add your ANTHROPIC_API_KEY")
            print("  3. Run this script again: python test_setup.py")
    
    print()
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

