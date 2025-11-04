---
name: root-cause-tracing
description: Trace bugs backward through execution stacks to find and fix original triggers
---

# Root Cause Tracing Skill

## Core Principle

**"Trace backward through the call chain until you find the original trigger, then fix at the source."**

Bugs manifesting deep in execution stacks require backward tracing to identify and fix the original trigger, not the symptom location.

## When to Apply This Skill

Use root-cause-tracing when:
- ✅ Errors occur deep in execution (not at entry points)
- ✅ Stack traces show lengthy call chains
- ✅ It's unclear where invalid data originated
- ✅ You need to identify which test or code path triggers problems
- ✅ The same error appears in multiple places (single source, multiple manifestations)

## The Five-Step Process

### Step 1: Observe the Symptom
Note **where** the error manifests:
- What is the error message?
- Which function/line shows the failure?
- What data is invalid at this point?

*Example: "TypeError: Cannot read property 'id' of undefined at line 250"*

### Step 2: Find Immediate Cause
Identify the code **directly** causing the failure:
- What operation failed? (null dereference, wrong type, missing property)
- What was the code expecting?
- What did it actually receive?

*Example: "Expected fileRecord to be an object, but it's undefined"*

### Step 3: Ask "What Called This?"
Work backward through the call stack:
- Which function called the failing function?
- What parameters did it pass?
- Did it validate those parameters?

*Example: "upload_file() passes file_id to get_file_details()"*

### Step 4: Keep Tracing Upward
Follow parameter values backward through the call chain:
- Where did that parameter come from?
- Was it modified along the way?
- At what point did it become invalid?

*Example: "file_id comes from db.flush() which didn't actually persist"*

### Step 5: Locate Original Trigger
Find the true source of invalid data or incorrect behavior:
- This is where invalid data is created, not where it fails
- This is where assumptions are violated
- This is where the fix belongs

*Example: "The real issue: db.commit() never runs in the upload endpoint"*

## Adding Instrumentation

When manual tracing isn't sufficient:

```python
# Add logging to see parameter values
def problem_function(file_id):
    print(f"DEBUG: file_id = {file_id}, type = {type(file_id)}")
    print(f"DEBUG: Stack trace: {import inspect; inspect.stack()}")
    # ... rest of function
```

**Always capture:**
- Directory paths (which working directory?)
- Working directories (os.getcwd())
- Environment variables (os.environ)
- Stack traces (new Error().stack in JS, inspect.stack() in Python)

**In tests, use `console.error()` or `print()` rather than loggers**, which may be suppressed during testing.

## Defense-in-Depth

After fixing the root cause, add validation at multiple layers to prevent similar issues:

```python
# Layer 1: Input validation (entry point)
if not file_id:
    raise ValueError("file_id cannot be empty")

# Layer 2: Assertion (internal check)
assert isinstance(file_id, int), "file_id must be integer"

# Layer 3: Explicit null check (before use)
if file_record is None:
    raise ValueError("File not found for ID: {file_id}")
```

## Key Warning ⚠️

**NEVER fix just the symptom location.**

Always trace to the source. Symptom fixes mask the real issue and create cascading failures.

### Anti-Pattern Example

```python
# WRONG: Symptom fix
if file_record is None:
    file_record = FileRecord()  # Create empty object to prevent crash

# RIGHT: Root cause fix
# Find WHERE file_record comes from
# Make sure db.query() actually returns something
# Validate the database returned what we expected
```

## Real-World Example: File Persistence Bug

**Symptom:** File upload returns 201 with file ID, but file doesn't persist to database

**Tracing Process:**
1. **Symptom:** SELECT query in list_patient_files returns 0 rows
2. **Immediate Cause:** File not in database table
3. **What called this?** upload_file() created FileModel and called db.add()
4. **Keep tracing:** db.add() was called, but was db.commit() called?
5. **Original Trigger:** No db.commit() in upload_file endpoint due to incorrect assumption about dependency override

**Fix:** Add explicit db.commit() in the endpoint, not in symptom location (the SELECT query)

## Integration with Other Skills

Works with:
- **systematic-debugging**: Use this for Phase 1 (Root Cause Investigation)
- **test-fixing**: Use together to fix test failures at their source
- **defense-in-depth**: Add validation layers after fixing root cause

---

*Source: obra/superpowers - root-cause-tracing skill*
*Installation: Project-scoped (.claude/skills/) - NO HOOKS*
*Safe to use: Pure methodology, no CLI interference*
