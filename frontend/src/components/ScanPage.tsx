import { useState, useEffect, useRef } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Check, RotateCcw, ChevronRight, Camera, ScanLine, Keyboard } from "lucide-react"
import { useNavigate } from "react-router-dom"
import { scanFace, type CubeState } from "../api/cube"

const SCAN_ORDER = [
  { name: "White", face: "U", hex: "#FFFFFF" },
  { name: "Yellow", face: "D", hex: "#FFD500" },
  { name: "Red", face: "R", hex: "#B71234" },
  { name: "Green", face: "F", hex: "#009E60" },
  { name: "Blue", face: "B", hex: "#0051BA" },
  { name: "Orange", face: "L", hex: "#FF5800" },
]

const COLOR_MAP: Record<string, string> = {
  W: "#FFFFFF", Y: "#FFD500", G: "#009E60",
  B: "#0051BA", O: "#FF5800", R: "#B71234",
}

const COLOR_CYCLE = ["W", "Y", "R", "G", "B", "O"]

const SOLVED_COLORS: Record<string, string> = {
  U: "W", D: "Y", R: "R", F: "G", B: "B", L: "O",
}

type Stage = "intro" | "camera" | "confirm" | "done"

function captureFrame(video: HTMLVideoElement): Promise<Blob | null> {
  return new Promise((resolve) => {
    const c = document.createElement("canvas")
    c.width = video.videoWidth
    c.height = video.videoHeight
    const ctx = c.getContext("2d")
    if (!ctx) { resolve(null); return }
    ctx.drawImage(video, 0, 0)
    c.toBlob((b) => resolve(b), "image/jpeg", 0.8)
  })
}

export default function ScanPage() {
  const navigate = useNavigate()
  const videoRef = useRef<HTMLVideoElement>(null)

  const [stage, setStage] = useState<Stage>("intro")
  const [faceIndex, setFaceIndex] = useState(0)
  const [colors, setColors] = useState<string[] | null>(null)
  const [faceResults, setFaceResults] = useState<Record<string, string[]>>({})
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [camStream, setCamStream] = useState<MediaStream | null>(null)
  const [capturedImage, setCapturedImage] = useState<string | null>(null)

  const current = SCAN_ORDER[faceIndex]

  useEffect(() => {
    if (videoRef.current && camStream) {
      videoRef.current.srcObject = camStream
    }
  }, [camStream])

  useEffect(() => {
    return () => {
      if (camStream) camStream.getTracks().forEach((t) => t.stop())
    }
  }, [camStream])

  async function startCamera() {
    setError(null)
    setStage("camera")
    try {
      const s = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: { ideal: "environment" }, width: { ideal: 640 }, height: { ideal: 480 } },
        audio: false,
      })
      setCamStream(s)
    } catch {
      setError("Camera not available on this device.")
      setCamStream(null)
      setStage("intro")
    }
  }

  function stopCamera() {
    if (camStream) {
      camStream.getTracks().forEach((t) => t.stop())
      setCamStream(null)
    }
  }

  async function handleCapture() {
    const video = videoRef.current
    if (!video || !video.videoWidth) return
    setBusy(true)
    setError(null)

    const blob = await captureFrame(video)
    if (!blob) { setBusy(false); return }

    const url = URL.createObjectURL(blob)
    setCapturedImage(url)

    try {
      const result = await scanFace(blob, current.face)
      setColors(result.colors)
      stopCamera()
      setStage("confirm")
    } catch (e) {
      setError(e instanceof Error ? e.message : "Scan failed — try again or set colors manually")
    } finally {
      setBusy(false)
    }
  }

  function handleEditColor(index: number) {
    if (!colors) return
    const next = [...colors]
    const idx = (COLOR_CYCLE.indexOf(next[index]) + 1) % COLOR_CYCLE.length
    next[index] = COLOR_CYCLE[idx]
    setColors(next)
  }

  function handleConfirm() {
    if (!colors) return
    setFaceResults((prev) => ({ ...prev, [current.face]: colors }))
    setCapturedImage(null)
    if (faceIndex < SCAN_ORDER.length - 1) {
      setFaceIndex((i) => i + 1)
      setColors(null)
      setStage("intro")
    } else {
      setStage("done")
    }
  }

  function handleSolve() {
    navigate("/solve-guide", { state: { cubeState: faceResults as unknown as CubeState } })
  }

  const progress = SCAN_ORDER.map((_, i) =>
    i < faceIndex ? "done" : i === faceIndex ? "current" : "pending"
  )

  return (
    <div className="min-h-screen bg-[#010101] text-white flex flex-col">
      <header className="flex items-center gap-3 px-6 py-5 border-b border-white/10">
        <button
          onClick={() => { stopCamera(); navigate("/") }}
          className="text-white/70 hover:text-white transition-colors"
        >
          <Camera size={20} />
        </button>
        <h1 className="font-garamond text-xl tracking-wider">Scan Cube</h1>
      </header>

      <main className="flex-1 flex flex-col items-center px-4 py-6">
        <div className="flex items-center gap-2 mb-6">
          {SCAN_ORDER.map((item, i) => (
            <div key={i} className="flex items-center gap-2">
              <div
                className={`w-7 h-7 rounded-full flex items-center justify-center text-[10px] uppercase font-medium transition-colors ${
                  progress[i] === "done" ? "bg-green-500/20 text-green-400"
                  : progress[i] === "current" ? "bg-white/15 text-white"
                  : "bg-white/5 text-white/30"
                }`}
                style={progress[i] === "current" ? { boxShadow: `0 0 0 1px ${item.hex}80` } : {}}
              >
                {progress[i] === "done" ? <Check size={12} /> : item.name[0]}
              </div>
              {i < 5 && (
                <div className={`w-3 h-px ${progress[i] === "done" ? "bg-green-500/40" : "bg-white/10"}`} />
              )}
            </div>
          ))}
        </div>

        <AnimatePresence mode="wait">
          {stage === "intro" && faceIndex === 0 && (
            <motion.div
              key="intro-setup"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center gap-5 pt-4 w-full max-w-sm"
            >
              <p className="text-white/90 text-sm text-center font-medium">How to hold your cube</p>
              <div className="bg-white/5 rounded-xl p-4 text-left w-full space-y-3">
                <div className="flex items-start gap-3">
                  <span className="text-white/50 text-xs font-mono mt-0.5">1.</span>
                  <p className="text-white/70 text-xs leading-relaxed">
                    Find the <strong className="text-white">white center</strong> piece and face it <strong className="text-white">up</strong> (toward the ceiling).
                  </p>
                </div>
                <div className="flex items-start gap-3">
                  <span className="text-white/50 text-xs font-mono mt-0.5">2.</span>
                  <p className="text-white/70 text-xs leading-relaxed">
                    Find the <strong className="text-white">green center</strong> piece and face it <strong className="text-white">toward you</strong>.
                  </p>
                </div>
                <div className="flex items-start gap-3">
                  <span className="text-white/50 text-xs font-mono mt-0.5">3.</span>
                  <p className="text-white/70 text-xs leading-relaxed">
                    This means: <strong className="text-white">White = Up</strong>, <strong className="text-white">Green = Front</strong>, <strong className="text-white">Red = Right</strong>, <strong className="text-white">Yellow = Down</strong>, <strong className="text-white">Blue = Back</strong>, <strong className="text-white">Orange = Left</strong>.
                  </p>
                </div>
              </div>
              <div className="bg-white/5 rounded-xl p-4 w-full">
                <p className="text-white/40 text-[10px] uppercase tracking-widest mb-2 text-center">Face layout (unfolded)</p>
                <div className="flex justify-center">
                  <div className="grid gap-[2px]" style={{ gridTemplateColumns: "repeat(4, 36px)", gridTemplateRows: "repeat(3, 36px)" }}>
                    <div />
                    <div className="rounded bg-white/10 flex items-center justify-center text-[10px] text-white/60" style={{gridRow:1,gridColumn:2}}>Up (W)</div>
                    <div />
                    <div />
                    <div className="rounded bg-white/10 flex items-center justify-center text-[10px] text-white/60" style={{gridRow:2,gridColumn:1}}>Left (O)</div>
                    <div className="rounded bg-white/10 flex items-center justify-center text-[10px] text-white/60" style={{gridRow:2,gridColumn:2}}>Front (G)</div>
                    <div className="rounded bg-white/10 flex items-center justify-center text-[10px] text-white/60" style={{gridRow:2,gridColumn:3}}>Right (R)</div>
                    <div className="rounded bg-white/10 flex items-center justify-center text-[10px] text-white/60" style={{gridRow:2,gridColumn:4}}>Back (B)</div>
                    <div />
                    <div className="rounded bg-white/10 flex items-center justify-center text-[10px] text-white/60" style={{gridRow:3,gridColumn:2}}>Down (Y)</div>
                    <div />
                    <div />
                  </div>
                </div>
              </div>
              <p className="text-white/30 text-xs text-center leading-relaxed">
                Keep this orientation in mind. For each face, rotate the cube so that face points at the camera.
              </p>
              <button
                onClick={startCamera}
                className="liquid-glass rounded-full w-full py-3.5 text-white/90 uppercase tracking-[0.2em] text-sm"
              >
                Open Camera
              </button>
              <button
                onClick={() => { setColors(Array(9).fill(SOLVED_COLORS[current.face])); stopCamera(); setCapturedImage(null); setStage("confirm") }}
                className="flex items-center gap-2 text-white/40 text-xs uppercase tracking-widest hover:text-white/70 transition-colors"
              >
                <Keyboard size={14} /> or tap to set colors manually
              </button>
            </motion.div>
          )}

          {stage === "intro" && faceIndex > 0 && (
            <motion.div
              key="intro-scan"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center gap-5 pt-4 w-full max-w-xs"
            >
              <div
                className="w-12 h-12 rounded-full flex items-center justify-center"
                style={{ backgroundColor: `${current.hex}15`, boxShadow: `0 0 0 1px ${current.hex}40` }}
              >
                <ScanLine size={22} style={{ color: current.hex }} />
              </div>
              <p className="text-center text-white/70 text-sm leading-relaxed">
                Now rotate your cube so the <strong className="text-white">{current.name}</strong> face
                points toward the camera, then tap <strong className="text-white">Capture</strong>.
              </p>
              <p className="text-white/30 text-xs text-center">
                Keep the cube in the same orientation, just tilt/rotate so {current.name} faces the lens.
              </p>
              {error && <p className="text-red-400 text-xs">{error}</p>}
              <button
                onClick={startCamera}
                className="liquid-glass rounded-full w-full py-3.5 text-white/90 uppercase tracking-[0.2em] text-sm"
              >
                Open Camera
              </button>
              <button
                onClick={() => { setColors(Array(9).fill(SOLVED_COLORS[current.face])); setCapturedImage(null); setStage("confirm") }}
                className="flex items-center gap-2 text-white/40 text-xs uppercase tracking-widest hover:text-white/70 transition-colors"
              >
                <Keyboard size={14} /> or tap to set colors manually
              </button>
            </motion.div>
          )}

          {stage === "camera" && (
            <motion.div
              key="camera"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="relative w-full max-w-sm bg-black rounded-2xl overflow-hidden mb-4"
              style={{ aspectRatio: "4/3" }}
            >
              {capturedImage && busy ? (
                <img src={capturedImage} className="absolute inset-0 w-full h-full object-cover" alt="captured" />
              ) : (
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  className="absolute inset-0 w-full h-full object-cover"
                />
              )}
              <div className="absolute inset-0 pointer-events-none flex items-center justify-center">
                <div className="w-[60%] aspect-square border-2 border-white/30 rounded-xl" />
              </div>
              {busy && (
                <div className="absolute inset-0 bg-black/60 flex items-center justify-center z-10">
                  <div className="w-7 h-7 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                </div>
              )}
              {error && (
                <div className="absolute top-3 left-3 right-3 z-10 bg-black/70 rounded-lg px-3 py-2 text-center">
                  <p className="text-red-400 text-xs mb-2">{error}</p>
                  <div className="flex gap-2 justify-center">
                    <button
                      onClick={() => { setError(null); setCapturedImage(null) }}
                      className="px-3 py-1 rounded-full bg-white/10 text-white/80 text-[10px] uppercase tracking-wider"
                    >
                      Try Again
                    </button>
                    <button
                      onClick={() => {
                        setColors(Array(9).fill(SOLVED_COLORS[current.face]))
                        stopCamera()
                        setStage("confirm")
                        setError(null)
                      }}
                      className="px-3 py-1 rounded-full bg-white/10 text-white/80 text-[10px] uppercase tracking-wider"
                    >
                      Set Manually
                    </button>
                  </div>
                </div>
              )}
              <button
                onClick={handleCapture}
                disabled={busy}
                className="absolute bottom-4 left-1/2 -translate-x-1/2 w-16 h-16 rounded-full bg-white/10 border-2 border-white/50 flex items-center justify-center disabled:opacity-40 z-10"
              >
                <div className="w-[52px] h-[52px] rounded-full bg-white" />
              </button>
            </motion.div>
          )}

          {stage === "confirm" && colors && (
            <motion.div
              key="confirm"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center gap-4 w-full max-w-xs pt-2"
            >
              <p className="text-white/50 text-xs uppercase tracking-widest">
                {current.name} Face
              </p>
              <p className="text-white/30 text-[10px] -mt-2 uppercase tracking-widest">
                tap sticker to cycle, or set all at once
              </p>
              <div className="grid grid-cols-3 gap-1 p-2 rounded-xl bg-black/30">
                {colors.map((color, i) => (
                  <button
                    key={i}
                    onClick={() => handleEditColor(i)}
                    className="w-[52px] h-[52px] sm:w-[60px] sm:h-[60px] rounded focus:outline-none active:scale-95 transition-transform"
                    style={{
                      backgroundColor: COLOR_MAP[color] || "#333",
                      boxShadow: "inset 0 0 4px rgba(0,0,0,0.5)",
                    }}
                  />
                ))}
              </div>
              <div className="flex gap-2">
                {COLOR_CYCLE.map((c) => (
                  <button
                    key={c}
                    onClick={() => setColors(Array(9).fill(c))}
                    className="w-7 h-7 rounded-full border border-white/20 focus:outline-none focus:ring-1 focus:ring-white/50 active:scale-90 transition-transform"
                    style={{ backgroundColor: COLOR_MAP[c] }}
                    aria-label={`Set all to ${c}`}
                  />
                ))}
              </div>
              {error && <p className="text-red-400 text-xs text-center">{error}</p>}
              <div className="flex gap-3">
                <button
                  onClick={() => { setColors(null); setError(null); setCapturedImage(null); setStage("intro") }}
                  className="flex items-center gap-1.5 px-5 py-2.5 rounded-full border border-white/15 text-white/60 text-xs uppercase tracking-widest hover:text-white transition-colors"
                >
                  <RotateCcw size={13} /> Retake
                </button>
                <button
                  onClick={handleConfirm}
                  className="flex items-center gap-1.5 px-5 py-2.5 rounded-full bg-white/10 text-white text-xs uppercase tracking-widest hover:bg-white/15 transition-colors"
                >
                  <Check size={13} /> Confirm
                </button>
              </div>
            </motion.div>
          )}

          {stage === "done" && (
            <motion.div
              key="done"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="flex flex-col items-center gap-6 pt-8 w-full max-w-xs"
            >
              <div className="w-16 h-16 rounded-full bg-green-500/15 flex items-center justify-center">
                <Check size={30} className="text-green-400" />
              </div>
              <p className="text-2xl font-garamond tracking-wide">All Scanned</p>
              <p className="text-white/50 text-sm text-center leading-relaxed">
                All 6 faces captured. Ready to compute the solution.
              </p>
              <button
                onClick={handleSolve}
                className="liquid-glass rounded-full w-full py-4 text-white/90 uppercase tracking-[0.2em] text-sm flex items-center justify-center gap-2"
              >
                Solve Cube <ChevronRight size={18} />
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  )
}
