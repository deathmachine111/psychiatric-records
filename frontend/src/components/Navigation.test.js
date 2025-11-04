import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/svelte'
import userEvent from '@testing-library/user-event'
import Navigation from './Navigation.svelte'

describe('Navigation Component', () => {
  it('renders app title', () => {
    const { container } = render(Navigation)
    expect(container.querySelector('h1')).toHaveTextContent('Psychiatric Records')
  })

  it('does not show back button when showBack is false', () => {
    const { queryByText } = render(Navigation, { props: { showBack: false } })
    expect(queryByText('Back')).toBeNull()
  })

  it('shows back button when showBack is true', () => {
    const { getByText } = render(Navigation, { props: { showBack: true } })
    expect(getByText(/Back/)).toBeInTheDocument()
  })

  it('dispatches backToList event when back button is clicked', async () => {
    const { component, getByText } = render(Navigation, { props: { showBack: true } })
    const user = userEvent.setup()

    let eventFired = false
    component.$on('backToList', () => {
      eventFired = true
    })

    await user.click(getByText(/Back/))
    expect(eventFired).toBe(true)
  })
})
