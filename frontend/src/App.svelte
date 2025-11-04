<script>
  import Navigation from './components/Navigation.svelte'
  import PatientList from './routes/PatientList.svelte'
  import PatientDetail from './components/PatientDetail.svelte'
  import TranscriptView from './components/TranscriptView.svelte'
  import Modal from './components/Modal.svelte'
  import PatientForm from './components/PatientForm.svelte'
  import ToastContainer from './components/ToastContainer.svelte'
  import { patients } from './stores/patients'
  import { ui } from './stores/ui'
  import { onMount } from 'svelte'

  let currentPage = 'list'
  let selectedPatient = null
  let selectedFile = null
  let patientFiles = []
  let showEditModal = false

  onMount(() => {
    // App initialization
    console.log('App mounted')
  })

  async function handleSelectPatient(e) {
    selectedPatient = e.detail
    currentPage = 'detail'
    // TODO: Load patient files from API
    patientFiles = []
  }

  function handleBackToList() {
    currentPage = 'list'
    selectedPatient = null
    selectedFile = null
    patientFiles = []
    showEditModal = false
  }

  function handleViewTranscript(e) {
    selectedFile = e.detail
    currentPage = 'transcript'
  }

  function handleBackToDetail() {
    currentPage = 'detail'
    selectedFile = null
  }

  async function handleFileUpload(e) {
    const uploadedFiles = e.detail
    try {
      // TODO: Connect to API endpoint for file upload
      ui.addToast(`${uploadedFiles.length} file(s) uploaded`, 'success')
      // Reload patient files
      // patientFiles = await fetchPatientFiles(selectedPatient.id)
    } catch (err) {
      ui.addToast('Failed to upload files', 'error')
    }
  }

  async function handleFileDelete(e) {
    const fileId = e.detail
    try {
      // TODO: Connect to API endpoint for file deletion
      patientFiles = patientFiles.filter(f => f.id !== fileId)
      ui.addToast('File deleted', 'success')
    } catch (err) {
      ui.addToast('Failed to delete file', 'error')
    }
  }

  async function handleEditSubmit(e) {
    const { name, notes } = e.detail

    try {
      await patients.updatePatient(selectedPatient.id, { name, notes })
      selectedPatient = { ...selectedPatient, name, notes }
      ui.addToast('Patient updated successfully', 'success')
      showEditModal = false
    } catch (err) {
      ui.addToast('Failed to update patient', 'error')
    }
  }

  function handleEditCancel() {
    showEditModal = false
  }

  function handleEditClick() {
    showEditModal = true
  }
</script>

<div class="min-h-screen bg-gray-50">
  <Navigation
    on:backToList={handleBackToList}
    showBack={currentPage === 'detail'}
  />

  <main class="max-w-6xl mx-auto p-6">
    {#if currentPage === 'list'}
      <PatientList on:selectPatient={handleSelectPatient} />
    {:else if currentPage === 'detail' && selectedPatient}
      <PatientDetail
        patient={selectedPatient}
        files={patientFiles}
        on:edit={handleEditClick}
        on:back={handleBackToList}
        on:upload={handleFileUpload}
        on:delete={handleFileDelete}
        on:selectFile={handleViewTranscript}
      />

      <Modal open={showEditModal} title="Edit Patient" on:close={() => (showEditModal = false)}>
        <PatientForm
          mode="edit"
          data={selectedPatient}
          on:submit={handleEditSubmit}
          on:cancel={handleEditCancel}
        />
      </Modal>
    {:else if currentPage === 'transcript' && selectedFile}
      <TranscriptView file={selectedFile} on:back={handleBackToDetail} />
    {/if}
  </main>

  <ToastContainer />
</div>

<style>
  :global(body) {
    margin: 0;
    padding: 0;
  }
</style>
