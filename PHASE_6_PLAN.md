# Phase 6: Frontend UI Development - Strategic Plan

## 🎯 Executive Summary

**Goal:** Build a functional, error-free Svelte UI for the psychiatric records system
**Approach:** TDD (Vitest) + Manual browser testing
**Timeline:** Modular, one component at a time
**Success Criteria:** All components render, accept input, call backend APIs, handle errors

---

## 🛠 Tech Stack Decisions

### Styling: Tailwind CSS
- ✅ **Why:** Utility-first = fast development, professional look, less CSS bugs
- ✅ **Setup:** `tailwind.config.js` + `postcss.config.js` + `global.css`
- ✅ **Commands:** Run `npm run dev` to see changes in real-time

### Testing: Vitest + @testing-library/svelte
- ✅ **Why:** Fast, isolated component tests, Svelte-native, hot reload
- ✅ **Setup:** `vitest.config.js` configured with jsdom
- ✅ **Commands:**
  - `npm run test` - Watch mode (interactive)
  - `npm run test:run` - Single run
  - `npm run test:ui` - Visual dashboard

### No External Component Library
- ✅ **Why:** Faster development, fewer dependencies, full control
- ✅ **Approach:** Build simple components with Tailwind
- ✅ **Reusable:** Modal, Button, Input, Card (Tailwind-based)

---

## 📦 Component Structure

```
frontend/src/
├── main.js                 # Entry point
├── App.svelte              # Root component + routing logic
├── global.css              # Tailwind + global styles
├── routes/
│   ├── +page.svelte        # Home/PatientList
│   ├── PatientForm.svelte   # Create/Edit patient
│   └── PatientDetail/
│       ├── +page.svelte    # Patient detail page
│       ├── FileList.svelte
│       └── FileUpload.svelte
├── components/
│   ├── Navigation.svelte
│   ├── PatientCard.svelte
│   ├── FileCard.svelte
│   ├── Modal.svelte
│   ├── Toast.svelte
│   └── Button.svelte (reusable)
├── stores/
│   ├── patients.ts         # Patient store (Svelte store)
│   ├── files.ts            # File store
│   └── ui.ts               # UI state (modals, toasts)
├── services/
│   ├── api.ts              # API calls (axios)
│   └── utils.ts            # Helper functions
└── __tests__/
    ├── PatientList.test.svelte
    ├── PatientForm.test.svelte
    ├── FileUpload.test.svelte
    └── ... (one test per component)
```

---

## 🧪 TDD Workflow (Per Component)

### Step 1: Write FAILING Test
```svelte
<!-- PatientList.test.svelte -->
<script>
  import { describe, it, expect } from 'vitest';
  import { render } from '@testing-library/svelte';
  import PatientList from '../routes/+page.svelte';

  describe('PatientList', () => {
    it('renders list of patients', () => {
      const { container } = render(PatientList);
      expect(container.querySelector('h1')).toHaveTextContent('Patients');
    });
  });
</script>
```

### Step 2: Run Test (FAILS)
```bash
npm run test
# ❌ FAIL: h1 "Patients" not found
```

### Step 3: Build Component (MINIMAL)
```svelte
<!-- routes/+page.svelte -->
<script>
  let patients = [];
</script>

<h1>Patients</h1>
<ul>
  {#each patients as patient (patient.id)}
    <li>{patient.name}</li>
  {/each}
</ul>
```

### Step 4: Test PASSES
```bash
npm run test
# ✅ PASS: PatientList renders
```

### Step 5: Add Props/Events
```svelte
<!-- Test for button click -->
it('calls onDelete when delete button clicked', async () => {
  // Add delete button test
});

<!-- Then add to component -->
<button on:click={() => onDelete(patient.id)}>Delete</button>
```

### Step 6: Test Passes, Move to Next Feature

---

## 📋 Phase 6 Breakdown: 5 Sprints

### Sprint 1: Core Patient Management (Days 1-2)
**Components:**
- `App.svelte` - Root layout + navigation
- `routes/+page.svelte` - PatientList
- `PatientCard.svelte` - Single patient display
- `Button.svelte` - Reusable button

**Tests:**
- PatientList renders with data
- PatientCard shows patient name, notes
- Button triggers click event

**Key Features:**
- Display patients from backend API
- Load patients on page mount
- Show patient name + creation date

---

### Sprint 2: Patient CRUD (Days 3-4)
**Components:**
- `PatientForm.svelte` - Create/Edit patient form
- `Modal.svelte` - Modal wrapper

**Tests:**
- Form renders
- Submit button sends data to API
- Modal opens/closes
- Form validation

**Key Features:**
- Create new patient
- Edit patient notes
- Modal for form

---

### Sprint 3: File Upload & Management (Days 5-6)
**Components:**
- `FileUpload.svelte` - Drag-drop upload
- `FileList.svelte` - List files for patient
- `FileCard.svelte` - Single file display

**Tests:**
- FileUpload accepts files
- Files display in list
- Delete file triggers API call

**Key Features:**
- Select patient
- Upload audio/image/text file
- Display uploaded files
- Show file metadata (upload date, type)

---

### Sprint 4: Processing & Status (Days 7-8)
**Components:**
- `ProcessingStatus.svelte` - Show Gemini processing state
- `RecordView.svelte` - Display transcribed content

**Tests:**
- Status shows "pending", "processing", "completed"
- Transcribed content displays
- Timestamps show correctly

**Key Features:**
- Process button triggers Gemini
- Show processing progress
- Display transcribed text
- Show processing timestamps

---

### Sprint 5: Export & Polish (Days 9-10)
**Components:**
- `NotionExportButton.svelte` - Export to Notion
- `Toast.svelte` - Notification messages

**Tests:**
- Export button sends to API
- Toast shows success/error message
- Message auto-dismisses

**Key Features:**
- One-click export to Notion
- Success/error notifications
- Error message handling

**Final Polish:**
- Responsive design (mobile + desktop)
- Error handling (API failures, network issues)
- Loading states (spinners, disabled buttons)
- Accessibility (basic: alt text, labels, semantic HTML)

---

## 🔌 API Integration Strategy

### Services Pattern
```typescript
// src/services/api.ts
import axios from 'axios';

const API = axios.create({
  baseURL: '/api',
  timeout: 10000,
});

export const patientsAPI = {
  list: () => API.get('/patients'),
  create: (data) => API.post('/patients', data),
  update: (id, data) => API.put(`/patients/${id}`, data),
  delete: (id) => API.delete(`/patients/${id}`),
};

export const filesAPI = {
  upload: (patientId, file, metadata) => {
    const fd = new FormData();
    fd.append('file', file);
    fd.append('metadata', metadata);
    return API.post(`/patients/${patientId}/files`, fd);
  },
  list: (patientId) => API.get(`/patients/${patientId}/files`),
  delete: (patientId, fileId) => API.delete(`/patients/${patientId}/files/${fileId}`),
  process: (patientId, fileId) => API.post(`/patients/${patientId}/process/${fileId}`),
};

export const notionAPI = {
  export: (patientId, fileId) => API.post(`/patients/${patientId}/export/${fileId}`),
  exportAll: (patientId) => API.post(`/patients/${patientId}/export-all`),
};
```

### Store Pattern
```typescript
// src/stores/patients.ts
import { writable } from 'svelte/store';
import { patientsAPI } from '../services/api';

function createPatientStore() {
  const { subscribe, set, update } = writable([]);

  return {
    subscribe,
    load: async () => {
      const response = await patientsAPI.list();
      set(response.data);
    },
    create: async (data) => {
      const response = await patientsAPI.create(data);
      update(patients => [...patients, response.data]);
    },
    delete: async (id) => {
      await patientsAPI.delete(id);
      update(patients => patients.filter(p => p.id !== id));
    },
  };
}

export const patients = createPatientStore();
```

---

## 🐛 Error Handling Strategy

### API Error Wrapper
```typescript
export async function handleAPICall(apiCall, errorContext) {
  try {
    return await apiCall();
  } catch (error) {
    const message = error.response?.data?.detail || 'Something went wrong';
    toast.error(`${errorContext}: ${message}`);
    console.error(errorContext, error);
    return null;
  }
}
```

### Component Error Handling
```svelte
<script>
  let error = null;
  let loading = false;

  async function handleSubmit() {
    loading = true;
    error = null;

    const result = await handleAPICall(
      () => patientsAPI.create(formData),
      'Failed to create patient'
    );

    if (result) {
      toast.success('Patient created');
      closeModal();
    }

    loading = false;
  }
</script>

<form on:submit|preventDefault={handleSubmit}>
  {#if error}
    <div class="bg-red-100 text-red-700 p-3 rounded">
      {error}
    </div>
  {/if}

  <button disabled={loading}>
    {loading ? 'Creating...' : 'Create Patient'}
  </button>
</form>
```

---

## ✅ Testing Checklist (Per Component)

- [ ] Component renders without error
- [ ] Props are correctly displayed
- [ ] User events (click, submit) trigger callbacks
- [ ] API calls are made with correct data
- [ ] Loading states show during API calls
- [ ] Error messages display on failure
- [ ] Component cleans up on unmount (no memory leaks)

---

## 🚀 Quick Start Commands

```bash
# Install dependencies (already done)
cd frontend
npm install

# Development server (with hot reload)
npm run dev
# → Open http://localhost:5173

# Run tests (watch mode)
npm run test

# Run tests (single run)
npm run test:run

# Build for production
npm run build

# Preview production build
npm run preview
```

---

## 📊 Success Metrics for Phase 6

| Metric | Target |
|--------|--------|
| Components built | 12+ |
| Tests per component | 3-5 |
| Test pass rate | 100% |
| Manual UI testing | All pages tested in browser |
| No console errors | ✅ Clean console |
| Backend API calls work | ✅ All endpoints hit correctly |
| Error handling | ✅ Graceful failures with user feedback |

---

## ⚠️ Known Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| Testing file uploads | Mock FormData, use vitest mock |
| Async state updates | Use `await` in tests, flush promises |
| Svelte reactivity | Use event handlers, update stores |
| CSS specificity | Use Tailwind classes only (no custom CSS) |
| CORS issues | Backend already configured proxy |

---

## 🎬 When to Ask for Help

- ❓ Svelte syntax confusion → Use `mcp-svelte-docs` MCP
- ❓ Tailwind styling issues → WebSearch for patterns
- ❓ Test failures → Debug with `console.log`, check test output
- ❓ API integration bugs → Check backend logs
- ❓ Performance issues → Use browser DevTools profiler

---

## 📝 Next Steps

1. ✅ **Setup complete:** Vitest, Tailwind, config files ready
2. 🎯 **Ready to code:** Start with Sprint 1 (PatientList)
3. 📋 **TDD pattern:** Write test → Build component → Manual test
4. ✅ **Commit regularly:** After each component sprint

---

*Phase 6 Plan Created: 2025-11-04*
*Status: READY TO BUILD* 🚀
