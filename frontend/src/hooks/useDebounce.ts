import { useEffect, useRef, useState } from 'react'

export function useDebounce<T>(value: T, delay = 400): T {
  const [debounced, setDebounced] = useState<T>(value)
  useEffect(() => {
    const id = setTimeout(() => setDebounced(value), delay)
    return () => clearTimeout(id)
  }, [value, delay])
  return debounced
}

export function useDebouncedCallback<T extends (...args: Parameters<T>) => void>(
  fn: T,
  delay = 400
): T {
  const ref = useRef(fn)
  ref.current = fn
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null)

  return ((...args: Parameters<T>) => {
    if (timer.current) clearTimeout(timer.current)
    timer.current = setTimeout(() => ref.current(...args), delay)
  }) as T
}
