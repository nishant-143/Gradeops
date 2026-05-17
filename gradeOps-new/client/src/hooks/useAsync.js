import { useCallback, useReducer, useRef, useState, useEffect } from 'react'

/**
 * Async state management hook with built-in loading, error, and retry logic
 */
export const useAsync = (asyncFunction, immediate = true) => {
  const [state, dispatch] = useReducer(
    (state, action) => {
      switch (action.type) {
        case 'PENDING':
          return { status: 'pending', data: null, error: null }
        case 'SUCCESS':
          return { status: 'success', data: action.payload, error: null }
        case 'ERROR':
          return { status: 'error', data: null, error: action.payload }
        default:
          return state
      }
    },
    { status: 'idle', data: null, error: null }
  )

  const executeCallback = useCallback(
    async (...args) => {
      dispatch({ type: 'PENDING' })
      try {
        const response = await asyncFunction(...args)
        dispatch({ type: 'SUCCESS', payload: response })
        return response
      } catch (error) {
        dispatch({ type: 'ERROR', payload: error })
        throw error
      }
    },
    [asyncFunction]
  )

  // Run immediately if requested
  const executeOnce = useRef(false)
  if (immediate && !executeOnce.current) {
    executeOnce.current = true
    executeCallback()
  }

  return { ...state, execute: executeCallback }
}

/**
 * Debounced state hook
 */
export const useDebouncedState = (initialValue, delay = 300) => {
  const [value, setValue] = useState(initialValue)
  const [debouncedValue, setDebouncedValue] = useState(initialValue)
  const timeoutRef = useRef(null)

  const setValueDebounced = useCallback(
    (newValue) => {
      setValue(newValue)
      clearTimeout(timeoutRef.current)
      timeoutRef.current = setTimeout(() => {
        setDebouncedValue(newValue)
      }, delay)
    },
    [delay]
  )

  return [debouncedValue, setValueDebounced, value]
}

/**
 * Local storage state hook with sync
 */
export const useLocalStorageState = (key, initialValue) => {
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = typeof window !== 'undefined' ? window.localStorage.getItem(key) : null
      return item ? JSON.parse(item) : initialValue
    } catch {
      return initialValue
    }
  })

  const setValue = useCallback(
    (value) => {
      try {
        const valueToStore = value instanceof Function ? value(storedValue) : value
        setStoredValue(valueToStore)
        if (typeof window !== 'undefined') {
          window.localStorage.setItem(key, JSON.stringify(valueToStore))
        }
      } catch (error) {
        console.error('Error storing value:', error)
      }
    },
    [key, storedValue]
  )

  return [storedValue, setValue]
}

/**
 * Previous value hook for tracking previous renders
 */
export const usePrevious = (value) => {
  const ref = useRef()
  
  useEffect(() => {
    ref.current = value
  }, [value])

  return ref.current
}
