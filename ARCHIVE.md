# 📦 CLAUDE.md Archive - Detailed Historical Documentation

**This file contains detailed documentation that was archived from CLAUDE.md for space optimization.**

**Current CLAUDE.md:** 787 lines (24 KB) - Essential information only
**ARCHIVE.md:** This file - Historical details, detailed tool documentation, session logs

---

## 🔍 Where to Find Information

| Topic | Location |
|-------|----------|
| **Project Status & Phase Completion** | PROJECT_STATUS.md (always authoritative) |
| **Testing Patterns & Lessons Learned** | TESTING_PATTERNS.md |
| **Test Scaffolding Templates** | TEST_SCAFFOLD_TEMPLATE.md |
| **Essential Development Rules** | CLAUDE.md (main file) |
| **Detailed Tools Documentation** | This file (ARCHIVE.md) |
| **Session History** | This file (ARCHIVE.md) |

---

## 🔧 Detailed Tools Documentation

### Available Tools - Full Reference

| Tool | Type | Installation | Token Cost | Best For |
|------|------|--------------|-----------|----------|
| **WebSearch** | Built-in | Always available | 1-2x | Planning phase, best practices research |
| **Sequential Thinking MCP** | MCP | Manual invocation | 3-5x ⚠️ | Complex debugging, deep analysis (reserve) |
| **GitHub MCP** | MCP | Manual invocation | Minimal | Framework source code, issue research |
| **systematic-debugging** | Claude Skill | Auto-activates | None | Bug investigation (4-phase methodology) |
| **root-cause-tracing** | Claude Skill | Auto-activates | None | Deep execution bugs (5-step backward trace) |
| **test-fixing** | Claude Skill | Auto-activates | None | Test failures (systematic resolution) |

### Strategic Web Search Methodology

**When to Search (Critical Timing):**

Research conducted at SPECIFIC points prevents most debugging:

**1. Planning Phase (Before Implementation)**
```
Timing: Before writing ANY code for a new feature
Search: "[Framework] [feature] best practices"
        "[Language] [pattern] common pitfalls"
Example: Before file upload: "FastAPI file upload SQLAlchemy testing best practices"
Result: Would find the :memory: SQLite issue immediately
Impact: Prevents 1-2 hours of debugging
```

**2. Hypothesis Formation (Before Testing)**
```
Timing: When you suspect something is wrong
Search: "[Observed behavior] [framework] transaction lifecycle"
Example: "SQLAlchemy session commit TestClient isolation"
Result: Would find the autocommit=False behavior immediately
Impact: Prevents 30-60 minutes of empirical testing
```

**3. Before Each "Leap of Faith"**
```
Timing: Before trying a creative fix that seems risky
Search: "[Fix idea] [framework] pattern"
Example: Before adding db.begin(): "SQLAlchemy commit db.begin() transaction"
Result: Validates approach before wasting time implementing it
Impact: Prevents 15-30 minutes of dead-end coding
```

**4. During Debugging (When Stuck > 10 Minutes)**
```
Timing: As soon as you have a concrete hypothesis
Search: Keep hypothesis specific, not vague
Example: "SQLite in-memory database connection pool isolation pytest"
Not: "why is my test failing" (too vague)
Result: Validates root cause, prevents further investigation of symptoms
Impact: Prevents 30-60 minutes chasing wrong causes
```

**Search Query Formula:**
```
[Specific Observation] + [Framework/Language] + [Pattern Name]

Good: "SQLAlchemy session state after commit TestClient FastAPI"
Bad: "database issue"

Good: "pytest fixture scope isolation database test"
Bad: "tests not working"
```

**Web Search Results Assessment:**
When you get search results, prioritize:
1. Official documentation (10x value vs blog posts)
2. GitHub issues showing exact problem (validate you're not alone)
3. Stack Overflow answers with explanations (understand why)
4. Medium/blog posts with code examples (implementation patterns)

### Claude Skills - Detailed Reference

#### 1. systematic-debugging (SKILL.md - 113 lines)
```
Location: .claude/skills/systematic-debugging/SKILL.md
Source: obra/superpowers (skill definition only, NO HOOKS)
Activation: Auto-triggers on bugs, test failures, unexpected behavior
```

**When to Use:**
- Encountering any bug or test failure
- Before proposing ANY fix (investigate first!)
- Time pressure situations (when quick fixes tempt you)
- Complex multi-component issues

**The Four Phases:**
1. Root Cause Investigation: Trace data flow to source
2. Pattern Analysis: Compare working vs broken code
3. Hypothesis & Testing: Form specific, testable hypotheses
4. Implementation: Address root causes, not symptoms

**Key Principle:** "NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST"

**Red Flags (Stop & Discuss):**
- Proposing solutions before tracing data flow
- Attempting multiple fixes simultaneously
- Third+ fix attempt after two failures (architectural problem)
- Skipping test writing

#### 2. root-cause-tracing (SKILL.md - 145 lines)
```
Location: .claude/skills/root-cause-tracing/SKILL.md
Source: obra/superpowers (skill definition only, NO HOOKS)
Activation: Auto-triggers on deep execution stack bugs
```

**When to Use:**
- Errors occur deep in execution (not entry points)
- Long stack traces with unclear origins
- Invalid data with unknown source
- Need to identify which test/code path triggers problem

**The Five-Step Process:**
1. Observe symptom (where does error appear?)
2. Find immediate cause (what code directly fails?)
3. Ask "What called this?" (work backward)
4. Keep tracing upward (follow parameters backward)
5. Locate original trigger (true source of problem)

**Adding Instrumentation:**
```python
# When manual tracing insufficient, add logging
print(f"DEBUG: file_id = {file_id}, type = {type(file_id)}")
print(f"DEBUG: Stack: {inspect.stack()}")
```

**Defense-in-Depth:**
After fixing root cause, add validation at multiple layers to prevent recurrence.

#### 3. test-fixing (SKILL.md - 79 lines)
```
Location: .claude/skills/test-fixing/SKILL.md
Source: mhattingpete/claude-skills-marketplace (skill definition only)
Activation: Auto-triggers on test failures
```

**When to Use:**
- Test suite failures
- Request: "fix these tests" or "make tests pass"
- After implementation, before commit

**Methodology:**
1. Execute test suite, catalog failures
2. Group by error type and module
3. Prioritize by impact and dependency order
4. Fix sequentially with validation
5. Run full suite to confirm no regressions

### MCP Servers - Technical Details

#### Sequential Thinking MCP (EXPENSIVE - Use Sparingly)
```
Connection: stdio transport (user scope)
Command: npx -y @modelcontextprotocol/inspector (test)
Status: Registered in settings.local.json
```

**When to Use:**
- Stuck on complex problem > 15 minutes
- Need deep systematic analysis
- Architecture decisions required
- Complex debugging requiring multiple hypotheses

**How to Use:**
```
Task tool with subagent_type="general-purpose"
Detailed prompt with full context
Expect 3-5x token consumption
Reserve for Phase 7+ or critical blockers
```

**Token Budget:** Max 2-3 uses before approaching limits
**Cost:** ~3-5x regular request tokens

#### GitHub MCP (MINIMAL COST - Use Freely)
```
Connection: HTTP transport (pre-configured)
Status: Available for code search and issues
```

**When to Use:**
- Framework source code investigation
- Find GitHub issues matching your problem
- Research patterns in public repositories
- Validate approaches before implementation

**How to Use:**
```
Use directly in conversation:
- Search code: search_code("pattern language:python")
- View issues: issue_read(method="get", owner="...", repo="...", issue_number=...)
- Examine commits: get_commit(owner="...", repo="...", sha="...")
```

**Token Cost:** Minimal (1-2x overhead)
**Usage:** Ad-hoc, no daily limit

### Critical Discovery: obra/superpowers Hooks Issue

**Root Cause Analysis:**

The obra/superpowers library includes a **`hooks/session-start.sh`** script that auto-executes at terminal startup. This caused:
- session.ssh file creation
- Terminal becoming unresponsive
- Claude Code CLI breaking
- Complete inability to use terminal commands

**Why It Happens:**
```
obra/superpowers structure:
├── hooks/
│   ├── session-start.sh  ← Auto-executes at CLI startup
│   ├── hooks.json        ← Defines hook triggers
│   └── ...
└── skills/
    ├── systematic-debugging/
    ├── root-cause-tracing/
    └── test-fixing/
```

When installed via plugin system, the **entire library** (including hooks) gets loaded.

**Solution: Skill Definitions Only**

Extract ONLY the skill SKILL.md files and install project-scoped:
```
.claude/skills/
├── systematic-debugging/SKILL.md  (pure methodology)
├── root-cause-tracing/SKILL.md    (pure methodology)
└── test-fixing/SKILL.md           (pure methodology)
```

**Result:**
- ✅ Get proven debugging methodologies
- ✅ Zero hook infrastructure
- ✅ No CLI interference
- ✅ No terminal issues
- ✅ Project-scoped (safe to rollback)

**Key Principle:**
> "Extract skill definitions from problematic libraries. Install as project-scoped SKILL.md files only. Never use the full library installation if hooks are present."

---

## 📝 Detailed Session History

### Session 1: Phase 3 Completion + Testing Analysis (2025-11-03)

**Achievements:**
- ✅ Phase 3: 20/20 tests passing (100%)
- ✅ Identified root cause: Transaction isolation with TestClient + :memory: SQLite
- ✅ Fixed through strategic debugging and hypothesis-driven methodology
- ✅ Created comprehensive TESTING_PATTERNS.md
- ✅ Created TEST_SCAFFOLD_TEMPLATE.md
- ✅ Updated CLAUDE.md with MCP and web search strategy

**Key Insights Documented:**
- Transaction lifecycle with SQLAlchemy autocommit=False
- Session management patterns for FastAPI TestClient
- Strategic web search methodology (timing and query formulation)
- When to use MCP servers vs traditional documentation

**Improvements for Phase 4+:**
- Use file-based SQLite for tests (not :memory:)
- Let dependency override manage commits (not route handlers)
- Call db.expire_all() before querying after flush/commit
- Search proactively before implementing (prevent 1-2 hours of debugging)
- Use TEST_SCAFFOLD_TEMPLATE.md for new test suites

**Technical Debt Resolved:**
- Debug logging cleaned up
- Path sanitization made consistent
- Session lifecycle properly documented
- Metadata sync verified with file integration

---

### Session 2: Phase 4 Initialization + Tool Setup (2025-11-04)

**Achievements:**
- ✅ Evaluated ApiDog for TDD (conclusion: not helpful for this project)
- ✅ Installed Sequential Thinking MCP (stdio, user scope)
- ✅ Installed GitHub MCP (pre-existing, HTTP)
- ✅ Updated CLAUDE.md with actual tools + token budgets
- ✅ Documented tool usage strategy (prevent hitting limits)
- ✅ Ready to start Phase 4: Image + Text Upload

**Tools Now Available:**
- Sequential Thinking MCP: Deep debugging (use sparingly, ~3-5x token cost)
- GitHub MCP: Framework source + issues (use freely, minimal cost)
- WebSearch: Planning phase, best practices (1-2x token cost)

**Token Budget Strategy:**
- WebSearch: ~1-2 per phase (planning only)
- GitHub MCP: Ad-hoc, no limit
- Sequential Thinking: Max 2-3 before hitting limits (reserved for Phase 5+)

**Phase 4 Ready:**
- Review TESTING_PATTERNS.md before writing tests
- Use TEST_SCAFFOLD_TEMPLATE.md for test structure
- WebSearch once at phase start for "FastAPI image/text upload best practices"
- Apply file validation patterns from Phase 2

---

### Session 3: Claude Skills Installation + obra/superpowers Discovery (2025-11-04)

**Critical Discovery:**
- 🔍 **Root Cause Found:** obra/superpowers library includes `hooks/session-start.sh` that auto-executes at terminal startup
- ⚠️ This hook infrastructure is WHY previous installation broke your CLI (session.ssh issue, terminal unresponsiveness)
- ✅ **Solution Validated:** Extract ONLY skill definitions, install project-scoped without hooks

**Achievements:**
- ✅ Installed 3 Claude Skills (systematic-debugging, root-cause-tracing, test-fixing)
- ✅ All installed project-scoped in `.claude/skills/` directory
- ✅ ZERO hooks infrastructure (pure SKILL.md methodology files)
- ✅ All 71 tests passing - no project impact
- ✅ CLI remains safe and functional
- ✅ Documented obra/superpowers hook issue for future reference

**What Was Installed:**
```
.claude/skills/
├── systematic-debugging/SKILL.md (113 lines)  - Four-phase debugging methodology
├── root-cause-tracing/SKILL.md   (145 lines)  - Backward call stack tracing
└── test-fixing/SKILL.md          (79 lines)   - Test failure resolution
```

**Why It's Safe:**
- Project-scoped (`.claude/skills/` not `~/.claude/skills/`)
- Pure methodology files (SKILL.md = thinking guides)
- NO hooks (obra's problematic `hooks/session-start.sh` excluded)
- NO subprocess management (no MCP overhead)
- NO configuration modification
- Zero system interference

**Skills Now Available:**
1. **systematic-debugging** - Auto-activates when bugs detected
2. **root-cause-tracing** - Auto-activates for deep execution bugs
3. **test-fixing** - Auto-activates on test failures

**Key Insight for Future Sessions:**
> "When installing from problematic libraries: Extract ONLY the SKILL.md definition files. Project-scope them in `.claude/skills/`. Ignore all hook infrastructure. Result: Get the methodology without the breaking changes."

---

### Session 4: Phase Completion Summary (2025-11-05)

**What Was Done:**
- ✅ Phase 1: Patient CRUD (13/13 tests)
- ✅ Phase 2: Audio Upload (20/20 tests)
- ✅ Phase 3: Metadata Input (20/20 tests)
- ✅ Phase 4: Image + Text Upload (5 tests extended)
- ✅ Phase 5: Gemini AI Processing (9/9 tests)
- ✅ Phase 5.5: Notion Export (9/9 tests)
- ✅ Phase 6: Frontend Component Testing (104/104 tests)

**Total: 175/175 tests passing (100%)**

**Status:** 78% complete (6 of 9 phases)

**Next: Phase 7 - Error Handling & UI Polish**

---

## 📊 Reference Information

### Phase 3 Testing Lessons (Complete Analysis)

**Pattern 1: Transaction Isolation with TestClient**
```
Problem: Data persists in route handler but disappears from test
Root Cause: :memory: SQLite + TestClient connection isolation
Solution Details: Use file-based SQLite (see TESTING_PATTERNS.md)
Prevention: Search before choosing test database
```

**Pattern 2: Route Handler Commit Interference**
```
Problem: db.commit() in route, then dependency override can't see data
Root Cause: autocommit=False starts new transaction after commit
Solution Details: Don't commit in route, let dependency override handle it
Prevention: Research FastAPI session management patterns upfront
```

**Pattern 3: SQLAlchemy Query Cache**
```
Problem: After flush/commit, query returns 0 results
Root Cause: Session caches query results, doesn't refetch after external updates
Solution Details: Call db.expire_all() before querying after other operations
Prevention: Understanding session lifecycle prevents this
```

**See TESTING_PATTERNS.md for Complete Details** - Captured 8 hours of debugging insights

---

## 🚀 Implementation Notes for Phase 7+

**Phase 7: Error Handling & UI Polish (4-8 hours)**
- Add error display UI improvements
- Implement user-friendly error messages
- Add progress indicator for Gemini processing
- Improve validation feedback

**Phase 8: Deployment to Fly.io (8-16 hours)**
- Create fly.toml configuration
- Setup environment variables
- Deploy backend + frontend
- Test in production

**Phase 9: Polish & Documentation (16+ hours)**
- Final QA pass
- Performance optimization
- Authentication implementation (OAuth2/JWT)
- API versioning
- Rate limiting

---

**Archive Last Updated:** 2025-11-05
**Corresponding CLAUDE.md Version:** 787 lines, 24 KB (41.8% reduction)
**File Compression:** Removed 565 lines of historical documentation, archived here

