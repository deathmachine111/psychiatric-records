# Phase 7: Error Handling & Process Monitoring - WITH PUPPETEER E2E TESTING

**Status:** READY TO IMPLEMENT
**Puppeteer MCP:** ✅ INSTALLED (v0.1.7)
**Approach:** TDD with automated e2e tests using Puppeteer

---

## 🎯 PHASE 7 OBJECTIVES (PUPPETEER-ENHANCED)

1. **Real-Time Process Monitoring** ⭐⭐⭐
   - Polling service that updates status every 1.5 seconds
   - No page refresh needed
   - User sees real-time feedback as file processes

2. **User-Friendly Error Messages** ⭐⭐⭐
   - Backend maps technical errors to user-readable messages
   - Error suggestions guide user next steps
   - Retry mechanism for transient errors

3. **Enhanced UI & Validation** ⭐⭐
   - ProcessingStatus component with animations
   - Form validation with real-time feedback
   - Loading states and disabled buttons

4. **Comprehensive E2E Testing** ⭐⭐⭐ (NEW WITH PUPPETEER)
   - Automated tests verify real user workflows
   - Tests cover: polling behavior, error handling, UI updates
   - No manual testing required (but recommended for final verification)

---

## 📋 PUPPETEER E2E TEST SUITE PLAN

### Test File Structure
```
frontend/src/e2e/
├── fileProcessing.e2e.js      (4 tests - core workflow)
├── errorHandling.e2e.js        (3 tests - error scenarios)
├── formValidation.e2e.js       (2 tests - input validation)
└── helpers/
    ├── testSetup.js            (server startup/shutdown)
    └── testHelpers.js          (common utilities)
```

### Test Specifications

**fileProcessing.e2e.js - Core Workflow Tests**

**Test 1: User can process audio file and see real-time status updates**
```javascript
// Setup: Start backend server, open app
// Action:
1. User uploads audio file (mp3)
2. Verifies file appears in list with "pending" status
3. Clicks "Process with Gemini" button
4. Watches for status change to "processing" (should happen within 2 seconds)
5. Waits for Gemini processing to complete (mock: return quick response)
6. Verifies status changes to "completed" WITHOUT page refresh
7. Verifies transcribed content appears

// Assertions:
✓ File appears in list immediately
✓ Status is "processing" within 2 seconds
✓ Status is "completed" after API response
✓ No page refresh occurs (URL unchanged)
✓ Transcribed content is visible

// Tools needed:
- puppeteer: navigate, click, waitForSelector, getProperty
- custom: waitForStatus(fileId, 'completed', timeout: 10s)
```

**Test 2: User can process image and see OCR results**
```javascript
// Similar to Test 1, but with image file
// Verifies image OCR workflow works end-to-end

// Assertions:
✓ Image appears in list
✓ Processing status visible
✓ OCR text appears without refresh
```

**Test 3: Polling stops after file completes**
```javascript
// Setup: Process file to completion
// Verification:
1. Start network monitoring in Puppeteer
2. Process file (status → completed)
3. Wait 5 seconds
4. Verify NO API calls to /processing-status after file completed

// Assertion:
✓ Polling stops automatically after status = "completed"
```

**Test 4: Multiple files can be processed independently**
```javascript
// Setup: Upload 2 files
// Action:
1. Start processing file 1
2. While file 1 is processing, start processing file 2
3. Watch both status updates independently
4. Verify file 1 completes without affecting file 2
5. Verify file 2 completes

// Assertions:
✓ Both files process independently
✓ Each file's status updates separately
✓ No interference between polling
```

---

**errorHandling.e2e.js - Error Scenario Tests**

**Test 5: User sees friendly error message when Gemini API fails**
```javascript
// Setup: Mock Gemini to return error
// Action:
1. Upload valid file
2. Click "Process"
3. Gemini returns error (e.g., "Invalid file format")
4. Wait for status to change to "failed"
5. Verify error message is visible and user-friendly

// Expected on screen:
"Could not process this audio file"
"Try a different file or check audio quality"
[Retry] button

// Assertions:
✓ Status changes to "failed" without refresh
✓ User-friendly error message visible
✓ Error message includes suggestion
✓ Retry button available
```

**Test 6: User can retry failed file processing**
```javascript
// Setup: File processing fails, then mock success
// Action:
1. File fails with error
2. User clicks [Retry] button
3. Gemini succeeds on second attempt
4. Verify status changes to "completed"

// Assertions:
✓ Retry button works
✓ Processing restarts
✓ Subsequent success updates status
```

**Test 7: Network error during polling is handled gracefully**
```javascript
// Setup: Simulate network failure during polling
// Action:
1. File is processing
2. Mock network error on one polling request
3. Verify polling continues (doesn't crash)
4. Verify error doesn't prevent completion

// Assertions:
✓ Transient network error doesn't crash app
✓ Polling recovers automatically
✓ Status updates continue
```

---

**formValidation.e2e.js - Input Validation Tests**

**Test 8: Patient form shows validation errors**
```javascript
// Action:
1. Click on Patient Name field and blur (empty)
2. Verify error message appears: "Patient name is required"
3. Type invalid chars (special chars) if applicable
4. Verify error message updates
5. Type valid name
6. Verify error clears and submit enables

// Assertions:
✓ Validation errors appear immediately
✓ Submit button disabled when invalid
✓ Submit button enabled when valid
```

**Test 9: File upload validates file types**
```javascript
// Action:
1. Try to upload unsupported file (.exe, .zip, etc)
2. Verify validation error appears
3. Try to upload supported file (.mp3, .jpg, .txt)
4. Verify file accepted

// Assertions:
✓ Unsupported files rejected with error
✓ Supported files accepted
✓ Error message is clear
```

---

## 🏗️ IMPLEMENTATION SEQUENCE (WITH PUPPETEER)

### Phase 7a: Core Monitoring (Hours 1-2)
1. **statusPoller.ts** - Polling service
2. **fileStatus.ts** - Reactive store
3. **Test with Puppeteer:** fileProcessing.e2e.js Test 1
4. Verify real polling works end-to-end

### Phase 7b: Error Handling (Hours 3-4)
1. **error_messages.py** - Error mapping
2. **Update processing.py** - Use error mapper
3. **ErrorMessage.svelte** - Enhanced display
4. **Test with Puppeteer:** errorHandling.e2e.js Tests 5-7
5. Verify error messages shown correctly

### Phase 7c: UI & Validation (Hours 5-6)
1. **ProcessingStatus.svelte** - Add animations
2. **FileList.svelte** - Subscribe to status
3. **PatientForm.svelte** - Add validation
4. **Test with Puppeteer:** formValidation.e2e.js Tests 8-9
5. Verify animations and validation work

### Phase 7d: Comprehensive Testing (Hours 7-8)
1. **fileProcessing.e2e.js Tests 2-4** - Advanced workflows
2. Manual testing (verify real Gemini works)
3. Performance testing (polling doesn't impact UI)
4. Documentation

---

## 🧪 PUPPETEER TEST INFRASTRUCTURE

### Test Setup
```javascript
// frontend/src/e2e/helpers/testSetup.js

beforeAll(async () => {
  // 1. Start backend server (port 8000)
  startBackendServer()

  // 2. Start frontend dev server (port 5173)
  startFrontendServer()

  // 3. Launch browser
  browser = await puppeteer.launch({
    headless: true,  // Use 'new' for new headless mode
    args: ['--no-sandbox']
  })

  // 4. Create page
  page = await browser.newPage()
})

afterAll(async () => {
  // Cleanup
  await browser.close()
  stopBackendServer()
  stopFrontendServer()
})

afterEach(async () => {
  // Clear database between tests
  resetTestDatabase()
})
```

### Puppeteer Test Helpers
```javascript
// frontend/src/e2e/helpers/testHelpers.js

// Wait for file status to change
export async function waitForStatus(page, fileId, status, timeoutMs = 10000) {
  return page.waitForFunction(
    (fId, s) => {
      const badge = document.querySelector(`[data-file-id="${fId}"] [data-status]`)
      return badge && badge.getAttribute('data-status') === s
    },
    { timeout: timeoutMs },
    fileId,
    status
  )
}

// Upload file programmatically
export async function uploadFile(page, patientId, filePath) {
  const input = await page.$('input[type="file"]')
  await input.uploadFile(filePath)
  await page.click('button:has-text("Upload")')
}

// Click process button
export async function processFile(page, fileId) {
  await page.click(`[data-file-id="${fileId}"] [data-action="process"]`)
}

// Get visible error message
export async function getErrorMessage(page) {
  return page.$eval('[role="alert"]', el => el.textContent)
}
```

---

## ✅ SUCCESS CRITERIA FOR PHASE 7

**All automated tests pass:**
- [ ] fileProcessing.e2e.js: 4/4 tests passing
- [ ] errorHandling.e2e.js: 3/3 tests passing
- [ ] formValidation.e2e.js: 2/2 tests passing
- **Total: 9/9 e2e tests passing**

**Vitest suite still passing:**
- [ ] All 104 frontend tests still passing
- [ ] All 71 backend tests still passing

**Manual verification (recommended):**
- [ ] Upload real audio file → see status update
- [ ] Force error scenario → see error message
- [ ] Retry failed file → works
- [ ] Form validation → works
- [ ] No console errors or warnings

**Performance:**
- [ ] Polling doesn't cause performance degradation
- [ ] No memory leaks from polling service
- [ ] Component updates smooth (no jank)

---

## 🔄 COMPARISON: PUPPETEER VS MANUAL TESTING

| Aspect | Manual Testing | Puppeteer E2E |
|--------|---|---|
| **Time to write tests** | 0 (skip) | 3 hours |
| **Time to run tests** | 15-20 min per test | 1 min all tests |
| **Catches timing bugs** | ❌ Miss 30% | ✅ Catch all |
| **Verifies UI rendering** | ❌ Manual observation | ✅ Automatic |
| **Can run after changes** | ❌ Tedious | ✅ One command |
| **Total Phase 7 time** | 12-14 hours | 10-12 hours |
| **Confidence in code** | Medium | High |

---

## 📊 PUPPETEER TOOLS AVAILABLE (11 tools)

From installed puppeteer-mcp-claude:
1. `navigate` - Go to URL
2. `click` - Click element
3. `type` - Type text
4. `screenshot` - Take screenshot
5. `getProperty` - Get element property
6. `waitForSelector` - Wait for element
7. `waitForFunction` - Wait for JS condition
8. `evaluate` - Run JavaScript
9. `close` - Close browser
10. `open` - Open browser
11. `getText` - Get element text

**All needed for Phase 7 testing** ✅

---

## 🚀 NEXT STEPS

1. ✅ Puppeteer MCP installed
2. ⏭️ Ready to implement Phase 7
3. **Need from you:**
   - Approve this plan?
   - Any adjustments?
   - Ready to start implementation?

**Recommendation:** Start with statusPoller.ts → immediately write fileProcessing.e2e.js Test 1 to verify polling works real-time

---

## 📝 ESTIMATED TIMELINE

- **Part A (Polling):** 2 hours
- **Part B (Error Handling):** 2 hours
- **Part C (UI):** 2 hours
- **Part D (Testing):** 2 hours
- **Buffer:** 2 hours
- **TOTAL:** 10 hours

**Delivery:** ~1.5 days of focused work → Phase 7 complete → ready for Phase 8 (Deployment)

