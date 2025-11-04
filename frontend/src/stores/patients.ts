import { writable, derived } from 'svelte/store'
import { patientsAPI } from '../services/api'

function createPatientStore() {
  const { subscribe, set, update } = writable<any[]>([])

  return {
    subscribe,
    loadPatients: async () => {
      try {
        const response = await patientsAPI.list()
        set(response.data)
        return response.data
      } catch (error) {
        console.error('Failed to load patients:', error)
        throw error
      }
    },
    createPatient: async (data: any) => {
      try {
        const response = await patientsAPI.create(data)
        update((patients) => [...patients, response.data])
        return response.data
      } catch (error) {
        console.error('Failed to create patient:', error)
        throw error
      }
    },
    updatePatient: async (id: number, data: any) => {
      try {
        const response = await patientsAPI.update(id, data)
        update((patients) =>
          patients.map((p) => (p.id === id ? response.data : p))
        )
        return response.data
      } catch (error) {
        console.error('Failed to update patient:', error)
        throw error
      }
    },
    deletePatient: async (id: number) => {
      try {
        await patientsAPI.delete(id)
        update((patients) => patients.filter((p) => p.id !== id))
      } catch (error) {
        console.error('Failed to delete patient:', error)
        throw error
      }
    },
  }
}

export const patients = createPatientStore()
