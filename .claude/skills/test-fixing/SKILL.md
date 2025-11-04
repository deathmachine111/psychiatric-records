---
name: test-fixing
description: Fix failing tests through intelligent error categorization and prioritized resolution
---

# Test Fixing Workflow

## Overview

The test-fixing workflow provides a structured approach for identifying and resolving failing tests through intelligent error categorization and prioritized remediation.

## Activation Criteria

This workflow activates when you:
- Request test fixes explicitly ("fix these tests", "make tests pass")
- Report test suite failures or CI/CD breakage
- Complete implementation and need test validation
- Use phrases indicating test problems ("tests aren't passing", "test suite is broken")

## Core Methodology

### Phase 1: Test Execution & Analysis
Execute the test suite and catalog all failures, noting:
- Error types (ImportError, AttributeError, AssertionError, etc.)
- Affected modules or test files
- Failure counts and patterns

### Phase 2: Error Classification
Group failures by:
- **Error category**: Type of failure
- **Source file or module**: Where the failure occurs
- **Underlying root cause**: What needs to be fixed

Rank groups by:
1. **Impact**: Number of tests affected
2. **Dependency order**: Foundational issues before dependent ones

### Phase 3: Sequential Resolution
For each prioritized group:
1. **Diagnose**: Root cause through code inspection and git diff review
2. **Implement**: Targeted fixes following project conventions
3. **Test**: Run the specific group to confirm resolution
4. **Validate**: Proceed only after group passes all tests

### Phase 4: Resolution Prioritization

Address failures in this sequence:
1. **Infrastructure issues**: Import errors, missing dependencies, configuration problems
2. **API changes**: Signature modifications, module reorganization, renamed identifiers
3. **Logic failures**: Assertion failures, business logic defects, edge cases

### Phase 5: Comprehensive Validation
Run the complete test suite to confirm:
- All fixes are effective
- No regressions were introduced
- Test coverage is maintained

## Key Principles

- **One at a time**: Address one error group before advancing
- **Incremental verification**: Verify subset tests pass after each fix
- **Minimal changes**: Keep fixes focused and targeted
- **Preserve coverage**: Maintain existing test coverage
- **Document patterns**: Note recurring issues for future prevention

## Usage

When you encounter failing tests, mention "test" or "failing" in your request to activate this workflow. The workflow will:

1. Execute tests and analyze failures
2. Group and prioritize failures intelligently
3. Fix issues systematically
4. Validate each fix with immediate re-testing
5. Ensure no regressions in the full test suite

---

*Source: mhattingpete/claude-skills-marketplace*
*Project-scoped installation for psychiatric-records project*
