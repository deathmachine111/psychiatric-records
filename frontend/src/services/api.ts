import axios from 'axios'

const API = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

// Patients API
export const patientsAPI = {
  list: () => API.get('/patients'),
  create: (data: any) => API.post('/patients', data),
  update: (id: number, data: any) => API.put(`/patients/${id}`, data),
  delete: (id: number) => API.delete(`/patients/${id}`),
  get: (id: number) => API.get(`/patients/${id}`),
}

// Files API
export const filesAPI = {
  list: (patientId: number) => API.get(`/patients/${patientId}/files`),
  upload: (patientId: number, file: File, metadata?: string) => {
    const fd = new FormData()
    fd.append('file', file)
    if (metadata) {
      fd.append('metadata', metadata)
    }
    return API.post(`/patients/${patientId}/files`, fd)
  },
  delete: (patientId: number, fileId: number) =>
    API.delete(`/patients/${patientId}/files/${fileId}`),
  get: (patientId: number, fileId: number) =>
    API.get(`/patients/${patientId}/files/${fileId}`),
}

// Processing API
export const processingAPI = {
  process: (patientId: number, fileId: number) =>
    API.post(`/patients/${patientId}/process/${fileId}`),
  status: (patientId: number) =>
    API.get(`/patients/${patientId}/processing-status`),
}

// Notion API
export const notionAPI = {
  export: (patientId: number, fileId: number) =>
    API.post(`/patients/${patientId}/export/${fileId}`),
  exportAll: (patientId: number) =>
    API.post(`/patients/${patientId}/export-all`),
}

export default API
