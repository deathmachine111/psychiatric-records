# Phase 7 Implementation Checklist - Ready to Start

**Status:** ✅ PUPPETEER MCP INSTALLED - READY TO CODE
**Estimated Duration:** 10 hours
**Test Suite:** 9 Puppeteer e2e tests + existing Vitest suite

---

## 📋 PART A: REAL-TIME STATUS MONITORING (2 hours)

### A.1 Create Polling Service
- [ ] Create `frontend/src/services/statusPoller.ts`
  - [ ] `startPolling(patientId, intervalMs = 1500)`
  - [ ] `stopPolling()`
  - [ ] `onStatusUpdate(callback)`
  - [ ] Handle network errors gracefully
  - [ ] Export pollingService singleton

- [ ] Create `frontend/src/stores/fileStatus.ts`
  - [ ] Writable store for file status
  - [ ] Subscribe to pollingService
  - [ ] Update on status changes
  - [ ] Track: status, error, lastUpdated

- [ ] **TEST:** Write `fileProcessing.e2e.js` Test 1
  - [ ] Upload file → see in list
  - [ ] Click Process → status becomes "processing"
  - [ ] Wait for completion → status becomes "completed"
  - [ ] Verify no page refresh
  - ✅ Expected: PASS

### A.2 Wire Components to Polling
- [ ] Update `frontend/src/components/PatientDetail.svelte`
  - [ ] Start polling on mount
  - [ ] Stop polling on unmount
  - [ ] Pass status to child components

- [ ] Update `frontend/src/components/FileList.svelte`
  - [ ] Subscribe to fileStatus store
  - [ ] Update processing_status reactively
  - [ ] Show real-time status badges

- [ ] Update `frontend/src/components/TranscriptView.svelte`
  - [ ] Subscribe to fileStatus
  - [ ] Auto-load transcribed_content when complete
  - [ ] Show error messages if failed

- [ ] **TEST:** fileProcessing.e2e.js Tests 2-4
  - [ ] Test 2: Image processing
  - [ ] Test 3: Polling stops after completion
  - [ ] Test 4: Multiple files process independently
  - ✅ Expected: All PASS

---

## 📋 PART B: USER-FRIENDLY ERROR HANDLING (2 hours)

### B.1 Create Error Message Service
- [ ] Create `backend/app/services/error_messages.py`
  - [ ] Map exception types to user messages
  - [ ] Provide suggestions for recovery
  - [ ] Include error codes for support
  - [ ] Handle: file not found, API timeouts, format errors, etc.

Example errors to handle:
```
Audio Transcription Failed → "Could not understand audio - try clearer recording"
Image OCR Failed → "Could not read text from image - try better quality"
File Not Found → "File is missing - may have been deleted"
Gemini Timeout → "Processing took too long - please try again"
Invalid File Format → "This file format is not supported"
```

### B.2 Update Backend Routes
- [ ] Update `backend/app/routes/processing.py`
  - [ ] Import error_messages service
  - [ ] Catch specific exceptions
  - [ ] Map to user-friendly messages
  - [ ] Return error with suggestion
  - [ ] Log detailed error for debugging

- [ ] Update error response format:
```json
{
  "detail": "Could not process this audio file",
  "suggestion": "Try a different file or check audio quality",
  "error_code": "AUDIO_TRANSCRIPTION_FAILED"
}
```

### B.3 Enhance Frontend Error Display
- [ ] Update `frontend/src/components/ErrorMessage.svelte`
  - [ ] Display main error message
  - [ ] Show suggestion text
  - [ ] Display error code for support
  - [ ] Add [Copy Details] button

- [ ] Update `frontend/src/stores/ui.ts`
  - [ ] Add toast messages for errors
  - [ ] Include suggestions in toasts
  - [ ] Auto-dismiss after 5 seconds

- [ ] **TEST:** errorHandling.e2e.js Tests 5-7
  - [ ] Test 5: User sees friendly error message
  - [ ] Test 6: User can retry failed file
  - [ ] Test 7: Network errors handled gracefully
  - ✅ Expected: All PASS

---

## 📋 PART C: UI ENHANCEMENTS & VALIDATION (2 hours)

### C.1 Enhance ProcessingStatus Component
- [ ] Update `frontend/src/components/ProcessingStatus.svelte`
  - [ ] Add spinner animation during "processing"
  - [ ] Show time elapsed
  - [ ] Show estimated time remaining (optional)
  - [ ] Add error icon + message for "failed"
  - [ ] Add success checkmark for "completed"

- [ ] Add animations with CSS
  - [ ] Spinner rotation
  - [ ] Color transitions
  - [ ] Smooth state changes

### C.2 Form Validation
- [ ] Create `frontend/src/services/validation.ts`
  - [ ] `validatePatientName(name)` → {valid, error}
  - [ ] `validateFileSize(file)` → {valid, error}
  - [ ] `validateFileType(file)` → {valid, error}
  - [ ] `validateMetadata(text)` → {valid, error}

- [ ] Update `frontend/src/components/PatientForm.svelte`
  - [ ] Real-time name validation on blur
  - [ ] Show error immediately
  - [ ] Disable submit when invalid
  - [ ] Enable submit when valid

- [ ] Update `frontend/src/components/FileUpload.svelte`
  - [ ] Validate file type on select
  - [ ] Show validation error if invalid
  - [ ] Validate file size
  - [ ] Show total size warning if near limit

- [ ] **TEST:** formValidation.e2e.js Tests 8-9
  - [ ] Test 8: Form validation shows errors
  - [ ] Test 9: File upload validates types
  - ✅ Expected: All PASS

### C.3 Retry Mechanism
- [ ] Add [Retry] button to failed files
  - [ ] Only show when status = "failed"
  - [ ] Triggers reprocessing
  - [ ] Resets error state

---

## 📋 PART D: TESTING & VERIFICATION (2 hours)

### D.1 Puppeteer E2E Tests
- [ ] Create `frontend/src/e2e/` directory structure
- [ ] Create `frontend/src/e2e/helpers/testSetup.js`
  - [ ] Start/stop backend server
  - [ ] Start/stop frontend server
  - [ ] Launch/close browser
  - [ ] Reset database between tests

- [ ] Create `frontend/src/e2e/helpers/testHelpers.js`
  - [ ] `waitForStatus(fileId, status, timeout)`
  - [ ] `uploadFile(patientId, filePath)`
  - [ ] `processFile(fileId)`
  - [ ] `getErrorMessage()`

- [ ] Create test files:
  - [ ] `frontend/src/e2e/fileProcessing.e2e.js` (4 tests)
  - [ ] `frontend/src/e2e/errorHandling.e2e.js` (3 tests)
  - [ ] `frontend/src/e2e/formValidation.e2e.js` (2 tests)

### D.2 Run All Tests
- [ ] Run Vitest suite
  - ✅ 104 frontend tests should pass
  - ✅ 71 backend tests should pass

- [ ] Run Puppeteer e2e tests
  - ✅ 9 e2e tests should pass
  - ✅ Total: 184 tests passing

- [ ] Manual verification (optional but recommended)
  - [ ] Start backend: `cd backend && uvicorn app.main:app --reload`
  - [ ] Start frontend: `cd frontend && npm run dev`
  - [ ] Test real workflow:
    - [ ] Create patient
    - [ ] Upload file
    - [ ] Process with Gemini
    - [ ] Watch status update in real-time
    - [ ] See transcribed content appear
  - [ ] Test error scenario:
    - [ ] Mock Gemini error
    - [ ] See error message
    - [ ] Click Retry
    - [ ] Verify processing restarts

### D.3 Documentation
- [ ] Update PROJECT_STATUS.md
  - [ ] Phase 7 complete
  - [ ] 184/184 tests passing
  - [ ] Update completion percentage

- [ ] Create PHASE_7_SUMMARY.md
  - [ ] What changed
  - [ ] How to test
  - [ ] Known limitations

---

## 🎯 SUCCESS CRITERIA

- [x] Puppeteer MCP installed ✅
- [ ] All 9 Puppeteer tests passing
- [ ] All 104 Vitest tests still passing
- [ ] All 71 backend tests still passing
- [ ] Real-time status updates working
- [ ] Error messages user-friendly
- [ ] Form validation working
- [ ] No console errors/warnings
- [ ] Manual testing successful

---

## 🚀 IMPLEMENTATION ORDER (RECOMMENDED)

Follow this sequence for fastest development:

**Hour 1:**
1. Create statusPoller.ts ← Foundation
2. Create fileStatus.ts ← Store
3. Write fileProcessing.e2e.js Test 1 ← Immediate feedback

**Hour 2:**
4. Wire PatientDetail, FileList, TranscriptView
5. Run Test 1 → should PASS
6. Write Tests 2-4 → run → should PASS

**Hour 3:**
7. Create error_messages.py
8. Update processing.py
9. Write errorHandling tests → run

**Hour 4:**
10. Enhance ProcessingStatus.svelte
11. Add form validation
12. Write formValidation tests → run

**Hour 5-6:**
13. Manual testing with real Gemini
14. Fix any issues
15. Documentation

**Total: 10-12 hours**

---

## 📞 QUESTIONS BEFORE STARTING

1. **Puppeteer Setup:** Should I run e2e tests locally or in CI/CD later?
2. **Error Messages:** Any specific error messages you want customized?
3. **Polling Interval:** 1500ms (1.5 seconds) okay, or adjust?
4. **Retry Logic:** Unlimited retries, or max attempts?
5. **Manual Testing:** Will you be available for final verification?

---

## ✨ EXPECTED OUTCOME

After Phase 7:
- ✅ User uploads file → sees "pending"
- ✅ User clicks Process → sees "processing" (with spinner)
- ✅ After 10-30 seconds → sees "completed" (with checkmark)
- ✅ Transcribed content appears (NO page refresh)
- ✅ If error → sees friendly message + suggestion
- ✅ User can click [Retry] → processing restarts
- ✅ All validated by 9 automated Puppeteer tests

**MVP Ready for Phase 8 (Deployment)** 🚀

