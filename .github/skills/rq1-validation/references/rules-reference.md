# PRPL Rules Reference

12 rules implemented. Source: QAM/QAMi/BBM rule sets from SW_QAMRuleSet_Tmplt.xlsm.

---

## PRPL 01.00.00 - BC Requested State

**Applies to**: BC/BX releases  
**Severity**: WARNING  
**Activated**: 2016-07-01

**Rule**: BC-R must be in "Requested" state at least 8 weeks before PVER planned delivery date.

**Logic**:
1. For each BC/BX assigned to user (not Canceled/Closed)
2. Get all mapped PVER/PVAR via Releasereleasemap (RRM)
3. For each PVER/PVAR with a planned date:
   - threshold = pver_planned_date - 8 weeks
   - If today >= threshold AND BC state != "Requested" ? violation

**Why**: Ensures Build Configurations are properly requested in time for integration into product versions.

**Fix**: Move BC to "Requested" state, or update PVER planned date if timeline changed.

---

## PRPL 02.00.00 - Workitem Planned Date

**Applies to**: Workitems  
**Severity**: WARNING  
**Activated**: 2016-07-01

**Rule**: Workitem in started/active state must have a planned date entered in planning tab.

**Logic**:
1. Check workitem is in active state (Requested, Planned, Developed, Committed, etc.)
2. Check if planned date is empty/null
3. If active but no planned date ? violation

**Why**: All active work must have schedule planning for proper tracking.

**Fix**: Enter planned date in the workitem's planning tab.

---

## PRPL 03.00.00 - Conflicted State

**Applies to**: Issues, Releases, Workitems (all types)  
**Severity**: WARNING  
**Activated**: 2016-07-01

**Rule**: Item must not remain in "Conflicted" state.

**Logic**:
1. Check lifecyclestate == "Conflicted"
2. If yes ? violation

**Why**: Conflicted state means a merge/sync conflict in RQ1 that blocks normal workflow. Must be resolved.

**Fix**: Open item in RQ1, resolve the conflict, and transition to proper state.

---

## PRPL 06.00.00 - IFD Defect Attributes

**Applies to**: IFD (Issue FD) with Category = "Defect"  
**Severity**: WARNING  
**Activated**: 2016-07-01

**Rule**: All defect detection/injection attribute fields must be filled for Bug Fix Issues.

**Logic**:
1. Only applies to IFD with Category = "Defect"
2. Only in states: Evaluated, Committed, Implemented (skip Canceled/Conflicted)
3. Check two attribute groups:

   **A. Detection Attributes** (all active states):
   - Defect Detection Location
   - Defect Detection Process
   - Defect Detection Organisation
   - Defect Detection Date

   **B. Injection/Correction Attributes** (Evaluated/Committed/Implemented):
   - Defective Work Product Type
   - Defect Classification
   - Defect Injection Organisation
   - Defect Injection Date

4. Any missing field ? violation (lists all missing fields)

**Why**: Proper defect tracking requires full metadata for root cause analysis and process improvement.

**Fix**: Open IFD in RQ1, fill in all empty defect attribute fields.

---

## PRPL 07.00.00 - BC Planned Date vs PST Delivery

**Applies to**: BC/BX releases  
**Severity**: WARNING  
**Activated**: 2016-07-01

**Rule**: BC planned date must not be later than the requested delivery date of any mapped PVER/PVAR.

**Logic**:
1. Skip BC if state is Canceled, Developed, Conflicted, or Closed
2. For each mapped PVER/PVAR (PST) via RRM:
   - Skip if RRM mapping state is Canceled/Conflicted
   - Compare BC planned date with PST requested delivery date
   - If BC planned date > PST delivery date ? violation

**Why**: BC must deliver before or on the PVER/PVAR integration deadline.

**Fix**: Either move BC planned date earlier, or negotiate a later delivery date with PVER/PVAR owner.

---

## PRPL 11.00.00 - IFD 5-Day SLA

**Applies to**: IFD (Issue FD) in "New" state  
**Severity**: WARNING  
**Activated**: 2016-07-01

**Rule**: IFD must be evaluated within 5 working days of being assigned to project.

**Logic**:
1. Only for IFD in "New" state (not yet evaluated)
2. Find project assignment date (from HistoryLog - when belongsToProject was set)
3. Fallback: use submitdate if no project assignment found
4. Count working days (Mon-Fri only) from assignment to today
5. If >= 5 working days ? violation

**Why**: Function Development must evaluate incoming defect reports promptly (5-day SLA commitment).

**Fix**: Evaluate the IFD (move to "Evaluated" state) or explain delay.

---

## PRPL 12.00.00 - IFD BC Closure

**Applies to**: IFD (Issue FD)  
**Severity**: WARNING  
**Activated**: 2016-07-01

**Rule**: IFD must be closed when ALL mapped BC-Releases are closed or cancelled.

**Logic**:
1. Get all BC releases mapped to this IFD (via IssueReleaseMap)
2. Check if ALL BCs are in Closed or Canceled state
3. If yes, check IFD state
4. If IFD is NOT in Closed/Implemented ? violation

**Why**: If all delivery vehicles (BCs) are closed, the defect fix should also be finalized.

**Fix**: Close or implement the IFD, or re-map to an active BC if work is ongoing.

---

## PRPL 13.00.00 - IFD BC Planned Date

**Applies to**: IFD (Issue FD)  
**Severity**: WARNING  
**Activated**: 2016-07-01

**Rule**: IFD must be Implemented or Closed after BC planned date has passed.

**Logic**:
1. Get all BC releases mapped to this IFD
2. For each BC, check if BC planned date is in the past
3. If any BC past planned date AND IFD still in early states (New/Evaluated/Committed) ? violation

**Why**: Once BC delivery date passes, the fix should already be implemented.

**Fix**: Implement and close the IFD, or update BC planned date if timeline shifted.

---

## PRPL 14.00.00 - IFD ISW Commitment

**Applies to**: IFD (Issue FD)  
**Severity**: WARNING  
**Activated**: 2016-07-01

**Rule**: IFD must be Committed when parent Issue-SW (ISW) is Committed.

**Logic**:
1. Skip if IFD is Canceled/Conflicted/Closed/Committed/Implemented
2. Check parent ISW (hasParent relationship)
3. If parent ISW state == "Committed" AND IFD state is New/Submitted/Evaluated ? violation

**Why**: When the software issue is committed for a release, its child defect fixes must also be committed.

**Fix**: Commit the IFD (transition to "Committed" state).

---

## PRPL 15.00.00 - Release Closure

**Applies to**: All Release types (BC, BX, FC, FX, PVER, PVAR)  
**Severity**: INFO  
**Activated**: 2016-07-01

**Rule**: Release must be closed after its planned date has passed.

**Logic**:
1. Skip if state is Canceled/Conflicted/Closed
2. Only checks: Planned or Developed states
3. If planned date is in the past AND state is still Planned/Developed ? violation

**Why**: Releases past their delivery date should be formally closed.

**Fix**: Close the release, or update planned date if delivery is genuinely delayed.

---

## PRPL 16.00.00 - Workitem Closure

**Applies to**: Workitems  
**Severity**: INFO  
**Activated**: 2016-07-01

**Rule**: Workitem must be closed after its planned date has passed.

**Logic**:
1. Check if workitem has a planned date
2. Check if planned date is in the past
3. If past planned date AND workitem NOT closed ? violation

**Why**: Similar to PRPL 15 but for generic workitems.

**Fix**: Close the workitem or update planned date.

---

## PRPL 18.00.00 - IFD ISW Commitment Delay

**Applies to**: IFD (Issue FD)  
**Severity**: WARNING  
**Activated**: 2016-07-01

**Rule**: IFD not committed 5 or more working days after parent ISW was committed.

**Logic**:
1. Same preconditions as PRPL 14 (IFD not yet committed, parent ISW committed)
2. Query ISW HistoryLog to find when ISW transitioned to "Committed"
3. Count working days (Mon-Fri) from ISW commit date to today
4. If >= 5 working days ? violation

**Why**: Escalated version of PRPL 14. After 5 days delay, this becomes a process compliance issue.

**Fix**: Commit the IFD immediately. Investigate why it took >5 days.

---

## Severity Levels

| Severity | Impact | Action |
|----------|--------|--------|
| WARNING | Affects pass rate calculation | Must fix before QAM review |
| INFO | Informational only | Good practice to fix, not mandatory |

## Rule Sets

| Set | Rules | Focus |
|-----|-------|-------|
| QAM | 01, 02, 03, 06, 07, 11, 12, 13, 14, 15, 16, 18 | Quality Assurance (all 12) |
| QAMi | 01, 02, 03, 06, 07, 11, 12, 13, 14, 18 | QAM interim (WARNING rules only) |
| BBM | 01, 07 | Build Block Metrics (BC-focused) |
