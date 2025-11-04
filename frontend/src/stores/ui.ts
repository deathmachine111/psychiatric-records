import { writable } from 'svelte/store'

export interface Toast {
  id: string
  message: string
  type: 'success' | 'error' | 'info'
}

function createUIStore() {
  const { subscribe, update } = writable<{
    toasts: Toast[]
    isLoading: boolean
  }>({
    toasts: [],
    isLoading: false,
  })

  return {
    subscribe,
    addToast: (message: string, type: 'success' | 'error' | 'info' = 'info') => {
      const id = Math.random().toString(36).substr(2, 9)
      update((state) => ({
        ...state,
        toasts: [...state.toasts, { id, message, type }],
      }))

      // Auto-remove after 3 seconds
      setTimeout(() => {
        update((state) => ({
          ...state,
          toasts: state.toasts.filter((t) => t.id !== id),
        }))
      }, 3000)

      return id
    },
    removeToast: (id: string) => {
      update((state) => ({
        ...state,
        toasts: state.toasts.filter((t) => t.id !== id),
      }))
    },
    setLoading: (isLoading: boolean) => {
      update((state) => ({ ...state, isLoading }))
    },
  }
}

export const ui = createUIStore()
