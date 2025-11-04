---
name: systematic-debugging
description: Four-phase framework for resolving technical issues before attempting fixes
---

# Systematic Debugging Skill

## Core Framework

The systematic-debugging skill provides a **four-phase framework** for resolving technical issues by finding root causes before proposing solutions.

## The Four Phases

### Phase 1: Root Cause Investigation
Before any fix attempt, you must:
- Read error messages carefully and completely
- Reproduce issues consistently (can you trigger it every time?)
- Check recent changes (what changed before the issue appeared?)
- Gather evidence in multi-component systems
- Trace data flow back to the source

**Ask:** Where is the invalid data coming from?

### Phase 2: Pattern Analysis
Find working examples and compare completely:
- Identify all differences between working and broken code
- Understand dependencies and state changes
- Check assumptions against actual behavior
- Look for patterns that reveal systemic issues

**Ask:** What changed from working to broken?

### Phase 3: Hypothesis and Testing
Form specific hypotheses, test minimally:
- Test with single variables, not multiple changes
- Verify results before proceeding to next hypothesis
- Document what each test reveals
- Stop when data supports a clear hypothesis

**Ask:** What is the actual root cause, not just a symptom?

### Phase 4: Implementation
Create failing test cases first, then implement:
- Address root causes, not symptoms
- Make single, focused fixes
- Verify solutions work without breaking other tests
- Add defensive validation at multiple layers

**Ask:** Does this fix the root cause, or just the symptom?

## Critical Principles

**PRIMARY RULE:** *"NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST"*

Symptom fixes create new bugs and waste time. This is non-negotiable.

### Red Flags (STOP and Discuss)

You're skipping the process if you:

1. **Propose solutions before tracing data flow** - No guessing, investigate first
2. **Attempt multiple fixes simultaneously** - Fix one thing at a time
3. **Make a third fix attempt after two failures** - This signals an architectural problem, not a coding problem
4. **Skip writing tests** - Tests reveal the actual issue, not your assumptions

When you hit these red flags, pause and discuss with the user rather than continuing to hack.

## When to Use This Skill

Apply this skill for:
- ✅ Test failures
- ✅ Production bugs
- ✅ Unexpected behavior
- ✅ Performance problems
- ✅ Build failures
- ✅ Integration issues
- ✅ **Especially** under time pressure (when "quick fixes" seem tempting)

## Integration with Other Skills

This skill works alongside:
- **root-cause-tracing**: For deep bugs in execution stacks
- **test-fixing**: For systematic test failure resolution
- **defense-in-depth**: Add validation at multiple layers after fixing

## Example Application

**Symptom:** File upload returns 201 but file doesn't appear in database

**Wrong Approach (Symptom Fixing):**
```
Add another query to check if file exists
Add logging to see what's in the database
Try different database commands
```

**Right Approach (Root Cause):**
```
Phase 1: Where do files go? Trace upload → save → database
Phase 2: Are files saving to disk? (Yes) Are they committing to DB? (No)
Phase 3: Why doesn't db.commit() run? (Dependency override doesn't commit)
Phase 4: Add explicit db.commit() in endpoint with error handling
```

## Key Quote

> "The root cause is never where the error appears. Trace backward until you find the original trigger, then fix there."

---

*Source: obra/superpowers - systematic-debugging skill*
*Installation: Project-scoped (.claude/skills/) - NO HOOKS*
*Safe to use: Pure methodology, no CLI interference*
