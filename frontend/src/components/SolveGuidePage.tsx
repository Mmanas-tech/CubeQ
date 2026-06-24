import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { ArrowLeft, ChevronLeft, ChevronRight, CheckCircle } from "lucide-react"
import { useNavigate, useLocation } from "react-router-dom"
import { solveCube, applyMoves, type CubeState, type SolveResult } from "../api/cube"

const COLOR_MAP: Record<string, string> = {
  W: "#FFFFFF", Y: "#FFD500", G: "#009E60",
  B: "#0051BA", O: "#FF5800", R: "#B71234",
}

const FACE_POS: Record<string, { row: number; col: number }> = {
  U: { row: 0, col: 1 },
  L: { row: 1, col: 0 },
  F: { row: 1, col: 1 },
  R: { row: 1, col: 2 },
  B: { row: 1, col: 3 },
  D: { row: 2, col: 1 },
}

export default function SolveGuidePage() {
  const navigate = useNavigate()
  const location = useLocation()
  const cubeState = (location.state as { cubeState?: CubeState } | undefined)?.cubeState

  const [solution, setSolution] = useState<SolveResult | null>(null)
  const [step, setStep] = useState(0)
  const [intermediateStates, setIntermediateStates] = useState<CubeState[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!cubeState) { navigate("/scan"); return }
    let cancelled = false

    ;(async () => {
      try {
        const res = await solveCube(cubeState)
        if (cancelled) return
        setSolution(res)

        if (!res.success) {
          setError(res.error || "Could not solve cube")
          setLoading(false)
          return
        }

        const states: CubeState[] = [cubeState]
        if (res.moves.length > 0) {
          for (const m of res.moves) {
            const prev = states[states.length - 1]
            const r = await applyMoves(prev, [m])
            if (r.state) states.push(r.state)
          }
        }
        if (!cancelled) setIntermediateStates(states)
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : "Failed to connect to solver")
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()

    return () => { cancelled = true }
  }, [])

  const moves = solution?.moves ?? []
  const total = moves.length
  const isSolved = total === 0 || step >= total

  return (
    <div className="min-h-screen bg-[#010101] text-white flex flex-col">
      <header className="flex items-center gap-3 px-6 py-5 border-b border-white/10">
        <button onClick={() => navigate("/scan")} className="text-white/70 hover:text-white transition-colors">
          <ArrowLeft size={20} />
        </button>
        <h1 className="font-garamond text-xl tracking-wider">Solution</h1>
        {solution?.method && (
          <span className="ml-auto text-[10px] uppercase tracking-widest text-white/30">
            {solution.method}
          </span>
        )}
      </header>

      <main className="flex-1 flex flex-col items-center px-4 py-8">
        {loading && (
          <div className="flex flex-col items-center gap-4 pt-16">
            <div className="w-8 h-8 border-2 border-white/20 border-t-white rounded-full animate-spin" />
            <p className="text-white/40 text-sm">Solving cube...</p>
          </div>
        )}

        {error && !loading && (
          <div className="flex flex-col items-center gap-4 pt-16">
            <p className="text-red-400 text-sm text-center max-w-xs">{error}</p>
            <button onClick={() => navigate("/scan")} className="text-white/50 underline text-xs">
              Back to scan
            </button>
          </div>
        )}

        {!loading && !error && solution?.success && (
          <>
            {isSolved ? (
              <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="flex flex-col items-center gap-6 pt-8">
                <div className="w-16 h-16 rounded-full bg-green-500/15 flex items-center justify-center">
                  <CheckCircle size={32} className="text-green-400" />
                </div>
                <p className="text-2xl font-garamond tracking-wide">Solved!</p>
                <p className="text-white/50 text-sm text-center max-w-xs">
                  {total > 0 && (
                    <>{solution.solve_time !== undefined && `${solution.solve_time}s · `}{total} moves</>
                  )}
                  {total === 0 && "Cube was already solved"}
                </p>
                <button onClick={() => navigate("/scan")} className="liquid-glass rounded-full px-8 py-3.5 text-white/90 uppercase tracking-widest text-sm">
                  Scan Another
                </button>
              </motion.div>
            ) : (
              <>
                <div className="flex items-center gap-2 mb-6">
                  <span className="text-white/40 text-xs uppercase tracking-widest">
                    Move {step + 1} / {total}
                  </span>
                  <div className="flex-1 w-32 h-1 rounded-full bg-white/10">
                    <div
                      className="h-full rounded-full bg-white/30 transition-all"
                      style={{ width: `${((step) / total) * 100}%` }}
                    />
                  </div>
                </div>

                <motion.div
                  key={step}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="mb-8"
                >
                  <div className="text-[64px] sm:text-[80px] font-light tracking-tight text-white font-garamond text-center leading-none">
                    {moves[step]}
                  </div>
                </motion.div>

                {intermediateStates[step] && (
                  <div className="mb-6 scale-[0.85] sm:scale-100">
                    <div
                      className="grid"
                      style={{
                        gridTemplateColumns: "repeat(4, auto)",
                        gridTemplateRows: "repeat(3, auto)",
                        gap: "2px",
                      }}
                    >
                      {Object.entries(FACE_POS).map(([face, pos]) => (
                        <div
                          key={face}
                          className="grid grid-cols-3 gap-px p-[3px] rounded-lg"
                          style={{
                            backgroundColor: "rgba(255,255,255,0.05)",
                            gridRow: pos.row + 1,
                            gridColumn: pos.col + 1,
                          }}
                        >
                          {intermediateStates[step][face].map((color, i) => (
                            <div
                              key={i}
                              className="w-[18px] h-[18px] sm:w-[24px] sm:h-[24px] rounded-sm"
                              style={{
                                backgroundColor: COLOR_MAP[color] || "#333",
                                boxShadow: "inset 0 0 2px rgba(0,0,0,0.35)",
                              }}
                            />
                          ))}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <p className="text-white/30 text-xs mb-6 text-center">
                  Perform this move on your cube, then tap Next.
                </p>

                <div className="flex items-center gap-4">
                  <button
                    onClick={() => setStep(Math.max(0, step - 1))}
                    disabled={step === 0}
                    className="flex items-center gap-1 px-5 py-2.5 rounded-full border border-white/15 text-white/60 text-xs uppercase tracking-widest disabled:opacity-30 hover:text-white transition-colors"
                  >
                    <ChevronLeft size={15} /> Prev
                  </button>
                  <button
                    onClick={() => setStep(Math.min(total, step + 1))}
                    className="liquid-glass flex items-center gap-1 px-6 py-2.5 rounded-full text-white/90 text-xs uppercase tracking-widest"
                  >
                    {step + 1 >= total ? "Finish" : "Next"} <ChevronRight size={15} />
                  </button>
                </div>
              </>
            )}
          </>
        )}
      </main>
    </div>
  )
}
