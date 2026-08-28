---
applyTo: "**/*.py"
description: "Enforces consistent output format for validation results across all models and users"
---

# Output Format Rules

When displaying or generating PRPL validation results, ALWAYS use this structure:

## Violation Entry Format

```
[<number>] PRPL <XX>.00.00 | <SEVERITY>
    Item:   <RQ1 ID>
    Title:  <item title, max 60 chars>
    Rule:   <one-line description>
    Detail: <what specifically is wrong>
```

## Severity Levels

- `WARNING` - Counts against pass rate. Must be fixed.
- `INFO` - Informational. No action required.

## Pass Rate Formula

```
pass_rate = (total_checks - warning_count) / total_checks * 100
```

## Rules for Consistent Output

1. Always show rule ID as `PRPL XX.00.00` format
2. Always separate WARNING and INFO counts
3. Always show pass rate as percentage with 1 decimal
4. Never truncate violation lists - show all
5. Group violations by rule number when >10 violations
6. Date format: YYYY-MM-DD HH:MM
7. Never add emoji or decorative characters to reports
