const API_BASE = '/api'

export interface CubeState {
  [face: string]: string[]
}

export interface SolveResult {
  success: boolean
  moves: string[]
  method: string | null
  move_count: number
  solve_time?: number
  error?: string
  solved_state?: CubeState
}

async function apiFetch<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, init)
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.error || body.detail || `Request failed (${res.status})`)
  }
  return res.json()
}

export async function fetchScrambled(numMoves = 20): Promise<{ state: CubeState; moves: string[] }> {
  return apiFetch(`${API_BASE}/scramble`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ num_moves: numMoves }),
  })
}

export async function solveCube(state: CubeState, timeout = 30): Promise<SolveResult> {
  return apiFetch(`${API_BASE}/solve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ state, timeout }),
  })
}

export async function fetchSolved(): Promise<{ state: CubeState }> {
  return apiFetch(`${API_BASE}/solved`)
}

export async function applyMoves(
  state: CubeState,
  moves: string[]
): Promise<{ state: CubeState; moves_applied: string[] }> {
  return apiFetch(`${API_BASE}/apply-move`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ state, moves }),
  })
}

export async function scanFace(imageBlob: Blob, face: string): Promise<{ face: string; colors: string[] }> {
  const formData = new FormData()
  formData.append('file', imageBlob, 'face.jpg')
  const res = await fetch(`${API_BASE}/scan-face?face=${face}`, { method: 'POST', body: formData })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.error || `Scan failed (${res.status})`)
  }
  return res.json()
}
