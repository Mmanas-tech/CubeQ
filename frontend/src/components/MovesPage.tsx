import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { ArrowLeft, ChevronLeft, ChevronRight } from "lucide-react"
import { useNavigate } from "react-router-dom"

const MOVES = [
  {
    name: "R",
    fullName: "Right",
    description: "Turn the right face clockwise (when looking at it).",
    affected: "Right face turns. Up→Front→Down→Back cycle on the right column.",
    colors: { face: "#B71234", adjacent: ["#FFFFFF", "#009E60", "#FFD500", "#0051BA"] },
  },
  {
    name: "R'",
    fullName: "Right Prime",
    description: "Turn the right face counter-clockwise.",
    affected: "Right face turns back. Up→Back→Down→Front cycle on the right column.",
    colors: { face: "#B71234", adjacent: ["#FFFFFF", "#0051BA", "#FFD500", "#009E60"] },
  },
  {
    name: "R2",
    fullName: "Right Double",
    description: "Turn the right face 180 degrees.",
    affected: "Right face spins half. Opposite faces swap on the right column.",
    colors: { face: "#B71234", adjacent: ["#FFD500", "#009E60", "#FFFFFF", "#0051BA"] },
  },
  {
    name: "L",
    fullName: "Left",
    description: "Turn the left face clockwise (when looking at it).",
    affected: "Left face turns. Up→Back→Down→Front cycle on the left column.",
    colors: { face: "#FF5800", adjacent: ["#FFFFFF", "#0051BA", "#FFD500", "#009E60"] },
  },
  {
    name: "L'",
    fullName: "Left Prime",
    description: "Turn the left face counter-clockwise.",
    affected: "Left face turns back. Up→Front→Down→Back cycle on the left column.",
    colors: { face: "#FF5800", adjacent: ["#FFFFFF", "#009E60", "#FFD500", "#0051BA"] },
  },
  {
    name: "L2",
    fullName: "Left Double",
    description: "Turn the left face 180 degrees.",
    affected: "Left face spins half. Opposite faces swap on the left column.",
    colors: { face: "#FF5800", adjacent: ["#FFD500", "#0051BA", "#FFFFFF", "#009E60"] },
  },
  {
    name: "U",
    fullName: "Up",
    description: "Turn the top face clockwise (when looking from above).",
    affected: "Up face turns. Front→Right→Back→Left cycle on the top row.",
    colors: { face: "#FFFFFF", adjacent: ["#009E60", "#B71234", "#0051BA", "#FF5800"] },
  },
  {
    name: "U'",
    fullName: "Up Prime",
    description: "Turn the top face counter-clockwise.",
    affected: "Up face turns back. Front→Left→Back→Right cycle on the top row.",
    colors: { face: "#FFFFFF", adjacent: ["#009E60", "#FF5800", "#0051BA", "#B71234"] },
  },
  {
    name: "U2",
    fullName: "Up Double",
    description: "Turn the top face 180 degrees.",
    affected: "Up face spins half. Opposite faces swap on the top row.",
    colors: { face: "#FFFFFF", adjacent: ["#0051BA", "#B71234", "#009E60", "#FF5800"] },
  },
  {
    name: "D",
    fullName: "Down",
    description: "Turn the bottom face clockwise (when looking from below).",
    affected: "Down face turns. Front→Left→Back→Right cycle on the bottom row.",
    colors: { face: "#FFD500", adjacent: ["#009E60", "#FF5800", "#0051BA", "#B71234"] },
  },
  {
    name: "D'",
    fullName: "Down Prime",
    description: "Turn the bottom face counter-clockwise.",
    affected: "Down face turns back. Front→Right→Back→Left cycle on the bottom row.",
    colors: { face: "#FFD500", adjacent: ["#009E60", "#B71234", "#0051BA", "#FF5800"] },
  },
  {
    name: "D2",
    fullName: "Down Double",
    description: "Turn the bottom face 180 degrees.",
    affected: "Down face spins half. Opposite faces swap on the bottom row.",
    colors: { face: "#FFD500", adjacent: ["#0051BA", "#FF5800", "#009E60", "#B71234"] },
  },
  {
    name: "F",
    fullName: "Front",
    description: "Turn the front face clockwise (as you look at it).",
    affected: "Front face turns. Up→Right→Down→Left cycle on the front edges.",
    colors: { face: "#009E60", adjacent: ["#FFFFFF", "#B71234", "#FFD500", "#FF5800"] },
  },
  {
    name: "F'",
    fullName: "Front Prime",
    description: "Turn the front face counter-clockwise.",
    affected: "Front face turns back. Up→Left→Down→Right cycle on the front edges.",
    colors: { face: "#009E60", adjacent: ["#FFFFFF", "#FF5800", "#FFD500", "#B71234"] },
  },
  {
    name: "F2",
    fullName: "Front Double",
    description: "Turn the front face 180 degrees.",
    affected: "Front face spins half. Opposite faces swap on the front edges.",
    colors: { face: "#009E60", adjacent: ["#FFD500", "#B71234", "#FFFFFF", "#FF5800"] },
  },
  {
    name: "B",
    fullName: "Back",
    description: "Turn the back face clockwise (when looking at the back).",
    affected: "Back face turns. Up→Left→Down→Right cycle on the back edges.",
    colors: { face: "#0051BA", adjacent: ["#FFFFFF", "#FF5800", "#FFD500", "#B71234"] },
  },
  {
    name: "B'",
    fullName: "Back Prime",
    description: "Turn the back face counter-clockwise.",
    affected: "Back face turns back. Up→Right→Down→Left cycle on the back edges.",
    colors: { face: "#0051BA", adjacent: ["#FFFFFF", "#B71234", "#FFD500", "#FF5800"] },
  },
  {
    name: "B2",
    fullName: "Back Double",
    description: "Turn the back face 180 degrees.",
    affected: "Back face spins half. Opposite faces swap on the back edges.",
    colors: { face: "#0051BA", adjacent: ["#FFD500", "#FF5800", "#FFFFFF", "#B71234"] },
  },
]

const COLOR_MAP: Record<string, string> = {
  W: "#FFFFFF", Y: "#FFD500", G: "#009E60",
  B: "#0051BA", O: "#FF5800", R: "#B71234",
}

function CubeDiagram({ move }: { move: typeof MOVES[0] }) {
  const isPrime = move.name.endsWith("'")
  const isDouble = move.name.endsWith("2")
  const face = move.name[0]

  const solvedU = ["W","W","W","W","W","W","W","W","W"]
  const solvedR = ["R","R","R","R","R","R","R","R","R"]
  const solvedF = ["G","G","G","G","G","G","G","G","G"]
  const solvedD = ["Y","Y","Y","Y","Y","Y","Y","Y","Y"]
  const solvedL = ["O","O","O","O","O","O","O","O","O"]
  const solvedB = ["B","B","B","B","B","B","B","B","B"]

  let u = [...solvedU], r = [...solvedR], f = [...solvedF], d = [...solvedD], l = [...solvedL], b = [...solvedB]

  if (face === "R") {
    if (isDouble) {
      r = ["R","R","R","R","R","R","R","R","R"]
      const tmpU = [u[2],u[5],u[8]]; u[2]=d[2]; u[5]=d[5]; u[8]=d[8]; d[2]=tmpU[0]; d[5]=tmpU[1]; d[8]=tmpU[2]
      const tmpF = [f[2],f[5],f[8]]; f[2]=b[6]; f[5]=b[3]; f[8]=b[0]; b[0]=tmpF[2]; b[3]=tmpF[1]; b[6]=tmpF[0]
    } else if (isPrime) {
      r = ["R","R","R","R","R","R","R","R","R"]
      const tmpU = [u[2],u[5],u[8]]; u[2]=f[2]; u[5]=f[5]; u[8]=f[8]; f[2]=d[2]; f[5]=d[5]; f[8]=d[8]
      d[2]=b[6]; d[5]=b[3]; d[8]=b[0]; b[0]=tmpU[2]; b[3]=tmpU[1]; b[6]=tmpU[0]
    } else {
      r = ["R","R","R","R","R","R","R","R","R"]
      const tmpU = [u[2],u[5],u[8]]; u[2]=b[6]; u[5]=b[3]; u[8]=b[0]; b[0]=d[2]; b[3]=d[5]; b[8]=d[8]
      d[2]=f[2]; d[5]=f[5]; d[8]=f[8]; f[2]=tmpU[0]; f[5]=tmpU[1]; f[8]=tmpU[2]
    }
  } else if (face === "U") {
    if (isDouble) {
      const tmpF = [f[0],f[1],f[2]]; f[0]=d[0]; f[1]=d[1]; f[2]=d[2]; d[0]=tmpF[0]; d[1]=tmpF[1]; d[2]=tmpF[2]
      const tmpR = [r[0],r[1],r[2]]; r[0]=l[0]; r[1]=l[1]; r[2]=l[2]; l[0]=tmpR[0]; l[1]=tmpR[1]; l[2]=tmpR[2]
    } else if (isPrime) {
      const tmpF = [f[0],f[1],f[2]]; f[0]=r[0]; f[1]=r[1]; f[2]=r[2]; r[0]=b[0]; r[1]=b[1]; r[2]=b[2]
      b[0]=l[0]; b[1]=l[1]; b[2]=l[2]; l[0]=tmpF[0]; l[1]=tmpF[1]; l[2]=tmpF[2]
    } else {
      const tmpF = [f[0],f[1],f[2]]; f[0]=l[0]; f[1]=l[1]; f[2]=l[2]; l[0]=b[0]; l[1]=b[1]; l[2]=b[2]
      b[0]=r[0]; b[1]=r[1]; b[2]=r[2]; r[0]=tmpF[0]; r[1]=tmpF[1]; r[2]=tmpF[2]
    }
  } else if (face === "F") {
    if (isDouble) {
      const tU = [u[6],u[7],u[8]]; u[6]=d[2]; u[7]=d[1]; u[8]=d[0]; d[0]=tU[2]; d[1]=tU[1]; d[2]=tU[0]
      const tR = [r[0],r[3],r[6]]; r[0]=l[8]; r[3]=l[5]; r[6]=l[2]; l[2]=tR[6]; l[5]=tR[3]; l[8]=tR[0]
    } else if (isPrime) {
      const tmpU = [u[6],u[7],u[8]]; u[6]=r[0]; u[7]=r[3]; u[8]=r[6]; r[0]=d[2]; r[3]=d[1]; r[6]=d[0]
      d[0]=l[8]; d[1]=l[5]; d[2]=l[2]; l[2]=tmpU[8]; l[5]=tmpU[7]; l[8]=tmpU[6]
    } else {
      const tmpU = [u[6],u[7],u[8]]; u[6]=l[8]; u[7]=l[5]; u[8]=l[2]; l[2]=d[0]; l[5]=d[1]; l[8]=d[2]
      d[0]=r[6]; d[1]=r[3]; d[2]=r[0]; r[0]=tmpU[6]; r[3]=tmpU[7]; r[6]=tmpU[8]
    }
  } else if (face === "L") {
    if (isDouble) {
      const tmpU = [u[0],u[3],u[6]]; u[0]=d[0]; u[3]=d[3]; u[6]=d[6]; d[0]=tmpU[0]; d[3]=tmpU[3]; d[6]=tmpU[6]
      const tmpF = [f[0],f[3],f[6]]; f[0]=b[8]; f[3]=b[5]; f[6]=b[2]; b[2]=tmpF[6]; b[5]=tmpF[3]; b[8]=tmpF[0]
    } else if (isPrime) {
      const tmpU = [u[0],u[3],u[6]]; u[0]=b[8]; u[3]=b[5]; u[6]=b[2]; b[2]=d[6]; b[5]=d[3]; b[8]=d[0]
      d[0]=f[0]; d[3]=f[3]; d[6]=f[6]; f[0]=tmpU[0]; f[3]=tmpU[3]; f[6]=tmpU[6]
    } else {
      const tmpU = [u[0],u[3],u[6]]; u[0]=f[0]; u[3]=f[3]; u[6]=f[6]; f[0]=d[0]; f[3]=d[3]; f[6]=d[6]
      d[0]=b[8]; d[3]=b[5]; d[6]=b[2]; b[2]=tmpU[6]; b[5]=tmpU[3]; b[8]=tmpU[0]
    }
  } else if (face === "D") {
    if (isDouble) {
      const tmpF = [f[6],f[7],f[8]]; f[6]=u[6]; f[7]=u[7]; f[8]=u[8]; u[6]=tmpF[6]; u[7]=tmpF[7]; u[8]=tmpF[8]
      const tmpR = [r[6],r[7],r[8]]; r[6]=l[6]; r[7]=l[7]; r[8]=l[8]; l[6]=tmpR[6]; l[7]=tmpR[7]; l[8]=tmpR[8]
    } else if (isPrime) {
      const tmpF = [f[6],f[7],f[8]]; f[6]=l[6]; f[7]=l[7]; f[8]=l[8]; l[6]=b[6]; l[7]=b[7]; l[8]=b[8]
      b[6]=r[6]; b[7]=r[7]; b[8]=r[8]; r[6]=tmpF[6]; r[7]=tmpF[7]; r[8]=tmpF[8]
    } else {
      const tmpF = [f[6],f[7],f[8]]; f[6]=r[6]; f[7]=r[7]; f[8]=r[8]; r[6]=b[6]; r[7]=b[7]; r[8]=b[8]
      b[6]=l[6]; b[7]=l[7]; b[8]=l[8]; l[6]=tmpF[6]; l[7]=tmpF[7]; l[8]=tmpF[8]
    }
  } else if (face === "B") {
    if (isDouble) {
      const tU = [u[0],u[1],u[2]]; u[0]=d[8]; u[1]=d[7]; u[2]=d[6]; d[6]=tU[2]; d[7]=tU[1]; d[8]=tU[0]
      const tR = [r[2],r[5],r[8]]; r[2]=l[6]; r[5]=l[3]; r[8]=l[0]; l[0]=tR[8]; l[3]=tR[5]; l[6]=tR[2]
    } else if (isPrime) {
      const tmpU = [u[0],u[1],u[2]]; u[0]=l[6]; u[1]=l[3]; u[2]=l[0]; l[0]=d[8]; l[3]=d[7]; l[6]=d[6]
      d[6]=r[2]; d[7]=r[5]; d[8]=r[8]; r[2]=tmpU[0]; r[5]=tmpU[1]; r[8]=tmpU[2]
    } else {
      const tmpU = [u[0],u[1],u[2]]; u[0]=r[2]; u[1]=r[5]; u[2]=r[8]; r[2]=d[8]; r[5]=d[7]; r[8]=d[6]
      d[6]=l[0]; d[7]=l[3]; d[8]=l[6]; l[0]=tmpU[2]; l[3]=tmpU[1]; l[6]=tmpU[0]
    }
  }

  const faces = [
    { stickers: u, label: "U", gridRow: 1, gridColumn: 2 },
    { stickers: l, label: "L", gridRow: 2, gridColumn: 1 },
    { stickers: f, label: "F", gridRow: 2, gridColumn: 2 },
    { stickers: r, label: "R", gridRow: 2, gridColumn: 3 },
    { stickers: b, label: "B", gridRow: 2, gridColumn: 4 },
    { stickers: d, label: "D", gridRow: 3, gridColumn: 2 },
  ]

  return (
    <div className="grid gap-[2px]" style={{ gridTemplateColumns: "repeat(4, 44px)", gridTemplateRows: "repeat(3, 44px)" }}>
      <div />
      {faces.map((f) => (
        <div
          key={f.label}
          className="grid grid-cols-3 gap-[1px] p-[2px] rounded"
          style={{ backgroundColor: "rgba(255,255,255,0.06)", gridRow: f.gridRow, gridColumn: f.gridColumn }}
        >
          {f.stickers.map((c, i) => (
            <div
              key={i}
              className="rounded-sm"
              style={{ backgroundColor: COLOR_MAP[c] || "#333", boxShadow: "inset 0 0 2px rgba(0,0,0,0.3)" }}
            />
          ))}
        </div>
      ))}
      <div />
      <div />
      <div />
      <div />
      <div />
    </div>
  )
}

export default function MovesPage() {
  const navigate = useNavigate()
  const [index, setIndex] = useState(0)
  const move = MOVES[index]

  return (
    <div className="min-h-screen bg-[#010101] text-white flex flex-col">
      <header className="flex items-center gap-3 px-6 py-5 border-b border-white/10">
        <button onClick={() => navigate("/")} className="text-white/70 hover:text-white transition-colors">
          <ArrowLeft size={20} />
        </button>
        <h1 className="font-garamond text-xl tracking-wider">Moves</h1>
      </header>

      <main className="flex-1 flex flex-col items-center px-4 py-6">
        <div className="flex items-center gap-2 mb-6">
          <span className="text-white/40 text-xs uppercase tracking-widest">
            {index + 1} / {MOVES.length}
          </span>
          <div className="flex-1 w-32 h-1 rounded-full bg-white/10">
            <div className="h-full rounded-full bg-white/30 transition-all" style={{ width: `${((index) / MOVES.length) * 100}%` }} />
          </div>
        </div>

        <AnimatePresence mode="wait">
          <motion.div
            key={index}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="flex flex-col items-center gap-5 w-full max-w-sm"
          >
            <div className="text-[56px] sm:text-[72px] font-light tracking-tight text-white font-garamond text-center leading-none">
              {move.name}
            </div>
            <p className="text-white/50 text-sm uppercase tracking-widest">{move.fullName}</p>

            <CubeDiagram move={move} />

            <p className="text-white/70 text-sm text-center leading-relaxed max-w-xs">
              {move.description}
            </p>
            <p className="text-white/40 text-xs text-center leading-relaxed max-w-xs">
              {move.affected}
            </p>
          </motion.div>
        </AnimatePresence>

        <div className="flex items-center gap-4 mt-6">
          <button
            onClick={() => setIndex(Math.max(0, index - 1))}
            disabled={index === 0}
            className="flex items-center gap-1 px-5 py-2.5 rounded-full border border-white/15 text-white/60 text-xs uppercase tracking-widest disabled:opacity-30 hover:text-white transition-colors"
          >
            <ChevronLeft size={15} /> Prev
          </button>
          <button
            onClick={() => setIndex(Math.min(MOVES.length - 1, index + 1))}
            disabled={index === MOVES.length - 1}
            className="flex items-center gap-1 px-5 py-2.5 rounded-full border border-white/15 text-white/60 text-xs uppercase tracking-widest disabled:opacity-30 hover:text-white transition-colors"
          >
            Next <ChevronRight size={15} />
          </button>
        </div>

        {index === MOVES.length - 1 && (
          <motion.button
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            onClick={() => navigate("/scan")}
            className="liquid-glass rounded-full px-8 py-3.5 mt-6 text-white/90 uppercase tracking-[0.2em] text-sm"
          >
            Scan & Solve
          </motion.button>
        )}
      </main>
    </div>
  )
}
