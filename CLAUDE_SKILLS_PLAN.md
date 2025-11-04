# Claude Code Skills Installation Plan & Safety Assessment

**Date**: 2025-11-04
**Status**: Phase 1 (test-fixing) - INSTALLED SAFELY
**Phase 2+**: Awaiting user decision on systematic-debugging and root-cause-tracing

---

## Executive Summary

Performed comprehensive research on Claude Code Skills installation. **One skill (test-fixing) has been safely installed from a trusted source.** However, the other two requested skills (systematic-debugging, root-cause-tracing) present a **significant risk** and have NOT been installed.

---

## Skills Research Findings

### Requested Skills

| Skill | Source | Status | Risk Level |
|-------|--------|--------|------------|
| **test-fixing** | mhattingpete/claude-skills-marketplace | ✅ INSTALLED | SAFE |
| **systematic-debugging** | obra/superpowers | ❌ NOT INSTALLED | 🔴 CRITICAL |
| **root-cause-tracing** | obra/superpowers | ❌ NOT INSTALLED | 🔴 CRITICAL |

### Risk Assessment - obra/superpowers Library

**Critical Concern**: The two remaining requested skills both come from the `obra/superpowers` library.

**User's Previous Experience**:
> "i had used obra superpowers previously, it broke the whole thing"

**Decision**: This library should NOT be used without explicit user authorization and understanding of the risk.

---

## What Was Installed: test-fixing Skill

**Source**: `mhattingpete/claude-skills-marketplace` (Alternative, community-maintained source)

**Installation Type**: Project-scoped (`.claude/skills/test-fixing/`)

**Rationale**:
1. From a different, safer source than obra/superpowers
2. Contains focused, single-responsibility workflow
3. Complements TDD approach already documented in CLAUDE.md
4. Low risk of side effects or unintended behavior

**Activation**: This skill will activate when Claude Code detects:
- Failing test suites
- Requests to fix tests
- Test validation phase in development

**Files Installed**:
```
.claude/
└── skills/
    └── test-fixing/
        └── SKILL.md
```

---

## Why systematic-debugging & root-cause-tracing Were NOT Installed

### Core Issue

Both skills source from `obra/superpowers`, which you previously reported as breaking your project:

```
User: "i had used obra superpowers previously, it broke the whole thing"
```

This is NOT a minor warning. Breaking a project is a severe outcome that warrants extreme caution before reinstallation.

### What Would Need to Happen

To proceed with installing these skills from obra/superpowers, we would need:

1. **Root Cause Analysis**: Understand EXACTLY what broke and why
2. **Version Verification**: Confirm obra/superpowers has been fixed since then
3. **Scoped Testing**: Install in isolated test environment first
4. **Explicit Approval**: User must review findings and approve proceeding

This aligns with your directive: "proceed cautiously"

---

## Options for Moving Forward

### Option A: Continue Without Them (Current)
**Pros**:
- Zero risk to project stability
- test-fixing skill covers test debugging
- CLAUDE.md already documents systematic debugging patterns
- Manual use of Sequential Thinking MCP available for complex analysis

**Cons**:
- Lose automated skill activation for those workflows

**Recommendation**: ✅ **SAFE DEFAULT**

### Option B: Search for Alternative Sources
**Approach**:
1. Search for alternative implementations of systematic-debugging and root-cause-tracing
2. Evaluate community-maintained versions (like mhattingpete's marketplace has others)
3. Consider building custom skills based on CLAUDE.md patterns

**Pros**:
- Get functionality without obra/superpowers risk
- Could be safer, lighter-weight implementations

**Cons**:
- Requires additional research and vetting
- May not be as feature-complete as obra versions

**Recommendation**: 💛 **INVESTIGATE IF DESIRED**

### Option C: Investigate obra/superpowers Directly
**Approach**:
1. Clone obra/superpowers repository
2. Review recent changes and fixes
3. Check if issues that broke your project have been addressed
4. Test in isolated environment before full installation

**Pros**:
- Access to full feature set if issues are fixed
- Community-maintained library

**Cons**:
- Significant time investment to investigate
- Still carries historical risk
- Requires deep code review to ensure safety

**Recommendation**: 🔴 **PROCEED ONLY WITH USER EXPLICIT APPROVAL**

---

## Safety Mechanisms Implemented

### 1. Project-Scoped Installation
- Skills installed in `.claude/skills/` (project directory)
- NOT in `~/.claude/skills/` (personal/global directory)
- Benefit: Changes isolated to this project, safe to remove

### 2. Git-Tracked Installation
- All skill files are committed to git
- Easy rollback with `git revert` if needed
- Complete audit trail of what was installed

### 3. Documentation
- This plan file explains every decision
- SKILL.md files are readable and auditable
- All rationale documented for future reference

### 4. Rollback Procedure (If Needed)

If skills cause issues, rollback is simple:

```bash
# Option 1: Remove just the problematic skill
rm -rf .claude/skills/test-fixing

# Option 2: Revert all Claude config changes
git revert <commit-hash>

# Option 3: Full reset (nuclear)
git reset --hard <previous-commit>
```

---

## Test-Fixing Skill Validation

### How to Verify Installation Works

The skill will be available in Claude Code when:
1. Any test failures are detected
2. You request: "fix these tests" or "make tests pass"
3. You mention "tests" in relation to failures

**Manual Test**:
```bash
# Run tests that should fail
pytest tests/ -k "nonexistent_test" 2>/dev/null || true

# Now ask Claude Code: "fix these tests"
# The test-fixing skill should activate
```

### Expected Behavior

When activated, Claude Code should:
1. Run the test suite and catalog failures
2. Group failures by error type and module
3. Prioritize by impact and dependency order
4. Fix sequentially with validation after each fix
5. Run full suite to confirm no regressions

---

## Next Steps

### Immediate (✅ Completed)
- [x] Research all three requested skills
- [x] Identify source and safety concerns
- [x] Install test-fixing from safe source
- [x] Document decision and rationale
- [x] Create rollback procedures

### User Decision Required
- [ ] **Option A** (Recommended): Accept current state, continue without obra skills
- [ ] **Option B**: Research alternative sources for the other two skills
- [ ] **Option C**: Investigate obra/superpowers directly (requires explicit approval)

---

## References

### Skills Documentation
- **test-fixing**: Project-scoped at `.claude/skills/test-fixing/SKILL.md`
- **Source**: https://github.com/mhattingpete/claude-skills-marketplace

### Alternative Resources
- **awesome-claude-skills**: https://github.com/BehiSecc/awesome-claude-skills
- **Claude Code Skills Docs**: https://docs.claude.com/en/docs/claude-code/skills
- **Awesome Claude Skills Collection**: https://github.com/travisvn/awesome-claude-skills

### Project Context
- **Debugging approach**: Documented in `CLAUDE.md` (Sections: "Expert Debugging & Root Cause Analysis")
- **Testing patterns**: Documented in `TESTING_PATTERNS.md` (Phases 1-3)
- **MCP tools available**: Sequential Thinking MCP for complex analysis (use sparingly)

---

## Conclusion

The test-fixing skill has been safely installed from a trusted source. The two skills from obra/superpowers have NOT been installed due to your previous negative experience with that library.

**The project is stable and functional with the current installation.**

Your approval is needed to proceed with either:
1. Accepting this state (Option A - Recommended)
2. Researching alternatives (Option B)
3. Investigating obra/superpowers (Option C - Requires explicit approval)

---

*Created: 2025-11-04*
*Installation Type: Project-scoped (.claude/skills/)*
*Risk Level: GREEN (Current state is safe)*
*Pending: User decision on proceeding options*
