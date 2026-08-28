#!/usr/bin/env python3
"""
Isolated test for PRPL Rule 18: IFD-ISW Commitment Delay
Tests if IFD is committed within 5 working days after attached ISW commitment.

Usage:
    python tests/test_rule_prpl_18_isolated.py
"""
import os
import sys
from datetime import datetime

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

sys.path.append('src')
from config import RQ1_TOOLNAME, RQ1_TOOLVERSION
from rules.rule_prpl_18_ifd_isw_commitment_delay import Rule_IFD_ISW_Commitment_Delay


# =============================================================================
# TEST CONFIGURATION
# =============================================================================

TEST_CASES = {
    "case_1_delayed": {
        "ifd_id": "RQONE04984940",
        "description": "IFD committed >5 days after ISW",
        "expected": "FAIL"
    },
    "case_2_on_time": {
        "ifd_id": "RQONE04958329", 
        "description": "IFD committed within 5 days",
        "expected": "PASS"
    },
    "case_3_not_committed": {
        "ifd_id": "RQONE04979880",
        "description": "IFD not yet committed",
        "expected": "FAIL"
    }
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def fetch_ifd_with_parent(client, ifd_id):
    """Fetch IFD with parent ISW information."""
    r = client.query(
        Issue,
        where=(IssueProperty.id == ifd_id),
        select=[
            IssueProperty.id,
            IssueProperty.lifecyclestate,
            IssueProperty.cq__Type,
            IssueProperty.dcterms__title,
            IssueProperty.category,
            "cq:hasParent{cq:id,cq:LifeCycleState,cq:Type}"
        ]
    )
    
    if not r.members:
        return None, None
    
    issue = r.members[0]
    
    # Extract IFD data
    issue_data = {
        'id': issue.id,
        'cq__Type': issue.cq__Type,
        'category': getattr(issue, 'category', ''),
        'lifecyclestate': issue.lifecyclestate,
        'dcterms__title': getattr(issue, 'dcterms__title', ''),
    }
    
    # Extract parent ISW data
    parent_isw_data = None
    hasparent = getattr(issue, 'hasparent', None)
    if hasparent:
        parent_isw_data = {
            'id': getattr(hasparent, 'id', 'UNKNOWN'),
            'lifecyclestate': getattr(hasparent, 'lifecyclestate', ''),
            'uri': getattr(hasparent, 'uri', None)
        }
    
    return issue_data, parent_isw_data


def run_test_case(client, case_name, test_config):
    """Run single test case."""
    print(f"\n{'='*70}")
    print(f"TEST: {case_name}")
    print(f"Description: {test_config['description']}")
    print(f"Expected: {test_config['expected']}")
    print(f"{'='*70}")
    
    ifd_id = test_config['ifd_id']
    
    # Fetch IFD data
    print(f"\n[1] Fetching IFD: {ifd_id}")
    issue_data, parent_isw_data = fetch_ifd_with_parent(client, ifd_id)
    
    if not issue_data:
        print(f"  ? IFD not found")
        return False
    
    print(f"  ? IFD found: {issue_data['id']}")
    print(f"    State: {issue_data['lifecyclestate']}")
    print(f"    Type: {issue_data['cq__Type']}")
    
    if parent_isw_data:
        print(f"  ? Parent ISW: {parent_isw_data['id']}")
        print(f"    State: {parent_isw_data['lifecyclestate']}")
    else:
        print(f"  ? No parent ISW found")
    
    # Execute Rule 18
    print(f"\n[2] Executing PRPL Rule 18")
    rule = Rule_IFD_ISW_Commitment_Delay(issue_data, parent_isw_data, client=client)
    result = rule.execute()
    
    actual = "PASS" if result.passed else "FAIL"
    match = "?" if actual == test_config['expected'] else "?"
    
    print(f"\n[3] Results")
    print(f"  Status: {actual} ({result.severity})")
    print(f"  Expected: {test_config['expected']}")
    print(f"  Match: {match}")
    print(f"\n  Details:")
    print(f"  {result.description.strip()}")
    
    return actual == test_config['expected']


# =============================================================================
# MAIN TEST RUNNER
# =============================================================================

def main():
    """Run all test cases."""
    print("\n" + "="*70)
    print("PRPL RULE 18: IFD-ISW Commitment Delay Test Suite")
    print("="*70)
    
    # Initialize RQ1 client
    print("\n[Setup] Connecting to RQ1...")
    client = Client(
        base_url=BaseUrl.PRODUCTIVE,
        username=os.getenv("RQ1_USER"),
        password=os.getenv("RQ1_PASSWORD"),
        toolname=RQ1_TOOLNAME,
        toolversion=RQ1_TOOLVERSION
    )
    print("  ? Connected")
    
    # Run test cases
    results = {}
    for case_name, test_config in TEST_CASES.items():
        passed = run_test_case(client, case_name, test_config)
        results[case_name] = passed
    
    # Summary
    print(f"\n{'='*70}")
    print("TEST SUMMARY")
    print(f"{'='*70}")
    
    total = len(results)
    passed = sum(results.values())
    failed = total - passed
    
    for case_name, passed_flag in results.items():
        status = "? PASS" if passed_flag else "? FAIL"
        print(f"  {status} - {case_name}")
    
    print(f"\nTotal: {total} | Passed: {passed} | Failed: {failed}")
    
    if failed > 0:
        print(f"\n? Some tests failed!")
        sys.exit(1)
    else:
        print(f"\n? All tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()

