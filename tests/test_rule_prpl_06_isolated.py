#!/usr/bin/env python3
"""
Isolated test for PRPL Rule 06: IFD Defect Attributes

Tests if Bug Fix IFDs (Category = Defect) have all required
defect detection and correction attributes filled.

Usage:
    python tests/test_rule_prpl_06_isolated.py

Test structure:
- TEST_CASES: Dictionary with IFD IDs and expected results
- fetch_ifd(): Helper to query RQ1 for IFD with all defect fields
- run_test_case(): Execute rule and compare expected vs actual
- main(): Connect to RQ1, run all tests, print summary
"""

import sys
import os
from pathlib import Path

# Setup environment
os.environ["CI_ENVIRONMENT"] = "1"
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from rq1 import BaseUrl, Client
from rq1.issue import Issue
from rq1.models import IssueProperty

# Add parent directory to path to import modules
parent_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(parent_dir))

from config import RQ1_TOOLNAME, RQ1_TOOLVERSION
from rules.rule_prpl_06_ifd_defect_attributes import Rule_Ifd_DefectAttributes

# =============================================================================
# TEST CONFIGURATION
# =============================================================================

TEST_CASES = {
    "case_1_complete": {
        "ifd_id": "RQONE04984940",  # Bugfix - Closed, all defect attributes filled
        "description": "IFD RQONE04984940 - all 8 defect attributes filled",
        "expected": "PASS"
    },
    "case_2_complete": {
        "ifd_id": "RQONE04844440",  # Bugfix - Closed, all defect attributes filled
        "description": "IFD RQONE04844440 - all 8 defect attributes filled",
        "expected": "PASS"
    }
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def fetch_ifd(client: Client, ifd_id: str) -> dict:
    """
    Fetch IFD data with all defect-related fields.
    
    Args:
        client: RQ1 Client instance
        ifd_id: IFD RQ1 number
    
    Returns:
        dict with IFD data or None if not found
    """
    
    try:
        print(f"  Querying RQ1 for IFD {ifd_id}...")
        
        # NOTE: Must use IssueProperty.* (not raw strings) - maps to correct OSLC alias e.g. cq:DefectClassification
        r = client.query(
            Issue,
            where=(IssueProperty.id == ifd_id),
            select=[
                IssueProperty.id,
                IssueProperty.dcterms__title,
                IssueProperty.cq__Type,
                IssueProperty.lifecyclestate,
                IssueProperty.category,
                # 8 defect fields (must use IssueProperty, raw strings don't work)
                IssueProperty.defectdetectionlocation,
                IssueProperty.defectdetectionprocess,
                IssueProperty.defectdetectionorga,
                IssueProperty.defectdetectiondate,
                IssueProperty.defectiveworkproducttype,
                IssueProperty.defectclassification,
                IssueProperty.defectinjectionorga,
                IssueProperty.defectinjectiondate
            ]
        )
        
        if not r.members:
            print(f"  [WARNING] IFD {ifd_id} not found")
            return None
        
        issue = r.members[0]
        
        # Convert to dict format expected by rule
        ifd_dict = {
            'id': issue.id,
            'dcterms__title': getattr(issue, 'dcterms__title', 'N/A'),
            'cq__Type': issue.cq__Type,
            'lifecyclestate': issue.lifecyclestate,
            'category': getattr(issue, 'category', 'N/A'),
            'defectdetectionlocation': getattr(issue, 'defectdetectionlocation', None),
            'defectdetectionprocess': getattr(issue, 'defectdetectionprocess', None),
            'defectdetectionorga': getattr(issue, 'defectdetectionorga', None),
            'defectdetectiondate': getattr(issue, 'defectdetectiondate', None),
            'defectiveworkproducttype': getattr(issue, 'defectiveworkproducttype', None),
            'defectclassification': getattr(issue, 'defectclassification', None),
            'defectinjectionorga': getattr(issue, 'defectinjectionorga', None),
            'defectinjectiondate': getattr(issue, 'defectinjectiondate', None)
        }
        
        print(f"  Found IFD: {ifd_dict.get('dcterms__title', 'N/A')}")
        print(f"    State: {ifd_dict.get('lifecyclestate', 'N/A')}")
        print(f"    Category: {ifd_dict.get('category', 'N/A')}")
        
        # Debug: Print all 8 defect fields
        print(f"\n  Defect Detection Attributes (4 fields):")
        print(f"    1. Detection Location:   {ifd_dict.get('defectdetectionlocation', 'NOT SET')}")
        print(f"    2. Detection Process:    {ifd_dict.get('defectdetectionprocess', 'NOT SET')}")
        print(f"    3. Detection Orga:       {ifd_dict.get('defectdetectionorga', 'NOT SET')}")
        print(f"    4. Detection Date:       {ifd_dict.get('defectdetectiondate', 'NOT SET')}")
        
        print(f"\n  Defect Correction Attributes (4 fields):")
        print(f"    5. Work Product Type:    {ifd_dict.get('defectiveworkproducttype', 'NOT SET')}")
        print(f"    6. Classification:       {ifd_dict.get('defectclassification', 'NOT SET')}")
        print(f"    7. Injection Orga:       {ifd_dict.get('defectinjectionorga', 'NOT SET')}")
        print(f"    8. Injection Date:       {ifd_dict.get('defectinjectiondate', 'NOT SET')}")
        
        return ifd_dict
    
    except Exception as e:
        print(f"  [ERROR] Failed to fetch IFD {ifd_id}: {e}")
        import traceback
        traceback.print_exc()
        return None


def run_test_case(client: Client, case_name: str, case_config: dict) -> bool:
    """
    Run a single test case.
    
    Args:
        client: RQ1 Client instance
        case_name: Test case name
        case_config: Test case configuration
    
    Returns:
        True if test passed, False otherwise
    """
    
    print(f"\n{'='*70}")
    print(f"TEST CASE: {case_name}")
    print(f"{'='*70}")
    print(f"Description: {case_config['description']}")
    print(f"IFD ID: {case_config['ifd_id']}")
    print(f"Expected: {case_config['expected']}")
    
    # Fetch IFD data
    ifd_data = fetch_ifd(client, case_config['ifd_id'])
    if not ifd_data:
        print(f"[FAIL] Could not fetch IFD data")
        return False
    
    # Execute rule
    print(f"\n  Executing Rule PRPL 06...")
    rule = Rule_Ifd_DefectAttributes(ifd_data)
    result = rule.execute()
    
    # Print result
    print(f"\n  Result:")
    print(f"    Passed: {result.passed}")
    print(f"    Severity: {result.severity}")
    print(f"    Title: {result.title}")
    print(f"    Description:")
    for line in result.description.split('\n'):
        print(f"      {line}")
    
    # Validate against expected result
    expected_pass = (case_config['expected'] == "PASS")
    actual_pass = result.passed
    
    test_passed = (expected_pass == actual_pass)
    
    print(f"\n{'='*70}")
    if test_passed:
        print(f"? TEST PASSED: {case_name}")
    else:
        print(f"? TEST FAILED: {case_name}")
        print(f"  Expected: {'PASS' if expected_pass else 'FAIL'}")
        print(f"  Actual: {'PASS' if actual_pass else 'FAIL'}")
    print(f"{'='*70}")
    
    return test_passed


# =============================================================================
# MAIN TEST RUNNER
# =============================================================================

def main():
    """Main test runner."""
    
    print("="*70)
    print("PRPL RULE 06 - ISOLATED TEST")
    print("IFD Defect Detection/Correction Attributes Validation")
    print("="*70)
    
    # Get RQ1 credentials from environment
    username = os.getenv('RQ1_USER')
    password = os.getenv('RQ1_PASSWORD')
    
    if not username or not password:
        print("\n[ERROR] RQ1 credentials not found in environment")
        print("Set RQ1_USER and RQ1_PASSWORD environment variables")
        sys.exit(1)
    
    # Connect to RQ1
    print(f"\nConnecting to RQ1 as {username}...")
    client = Client(
        base_url=BaseUrl.PRODUCTIVE,
        username=username,
        password=password,
        toolname=RQ1_TOOLNAME,
        toolversion=RQ1_TOOLVERSION
    )
    
    # Run all test cases
    results = {}
    for case_name, case_config in TEST_CASES.items():
        try:
            passed = run_test_case(client, case_name, case_config)
            results[case_name] = passed
        except Exception as e:
            print(f"\n[ERROR] Test case {case_name} threw exception: {e}")
            results[case_name] = False
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed_count = sum(1 for passed in results.values() if passed)
    total_count = len(results)
    
    for case_name, passed in results.items():
        status = "? PASS" if passed else "? FAIL"
        print(f"{status} : {case_name}")
    
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    # Exit with appropriate code
    if passed_count == total_count:
        print("\n?? All tests passed!")
        sys.exit(0)
    else:
        print(f"\n? {total_count - passed_count} test(s) failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
