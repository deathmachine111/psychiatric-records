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

    // Load patient files from API
    try {
      ui.setLoading(true)
      const { filesAPI } = await import('./services/api')
      const response = await filesAPI.list(selectedPatient.id)
      patientFiles = response.data || []
    } catch (err) {
      console.error('Failed to load files:', err)
      ui.addToast('Failed to load patient files', 'error')
      patientFiles = []
    } finally {
      ui.setLoading(false)
    }
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
      ui.setLoading(true)
      const { filesAPI } = await import('./services/api')

      // Upload each file
      for (const file of uploadedFiles) {
        await filesAPI.upload(selectedPatient.id, file)
      }

      // Reload patient files
      const response = await filesAPI.list(selectedPatient.id)
      patientFiles = response.data || []
      ui.addToast(`${uploadedFiles.length} file(s) uploaded successfully`, 'success')
    } catch (err) {
      console.error('File upload error:', err)
      ui.addToast('Failed to upload files', 'error')
    } finally {
      ui.setLoading(false)
    }
  }

  async function handleFileDelete(e) {
    const fileId = e.detail
    try {
      ui.setLoading(true)
      const { filesAPI } = await import('./services/api')

      await filesAPI.delete(selectedPatient.id, fileId)
      patientFiles = patientFiles.filter(f => f.id !== fileId)
      ui.addToast('File deleted successfully', 'success')
    } catch (err) {
      console.error('File delete error:', err)
      ui.addToast('Failed to delete file', 'error')
    } finally {
      ui.setLoading(false)
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
