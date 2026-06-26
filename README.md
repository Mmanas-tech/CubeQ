<div align="center">

<br />

```
   ██████╗██╗   ██╗██████╗ ███████╗██╗ ██████╗
  ██╔════╝██║   ██║██╔══██╗██╔════╝██║██╔═══██╗
  ██║     ██║   ██║██████╔╝█████╗  ██║██║   ██║
  ██║     ██║   ██║██╔══██╗██╔══╝  ██║██║▄▄ ██║
  ╚██████╗╚██████╔╝██████╔╝███████╗██║╚██████╔╝
   ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝ ╚══▀▀═╝
```

**Scan. Solve. Smile.**

Point your camera at a scrambled Rubik's Cube — CubeIQ reconstructs its state using computer vision and generates an optimal solution using Kociemba's two-phase algorithm in seconds.

<br />

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React_18-20232A?style=flat-square&logo=react&logoColor=61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=flat-square&logo=opencv&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

<br />

</div>

---

## What is CubeIQ?

CubeIQ is a full-stack web application that solves any scrambled Rubik's Cube in three steps:

1. **Scan** — Point your camera at each of the 6 faces. OpenCV reads HSV values and maps sticker colors automatically.
2. **Solve** — Kociemba's two-phase algorithm computes an optimal solution — typically 18–25 moves in under 15 seconds.
3. **Follow** — A visual step-by-step guide walks you through every move with a live cube net showing the state after each step.

Built as a portfolio project demonstrating computer vision, algorithm design, full-stack architecture, and clean software engineering.

---

## Features

```
 📷  Camera scanning     →  HSV color detection + contour-based face alignment
 ✏️  Manual input        →  Tap any sticker to cycle its color if camera misses
 ⚡  Kociemba solver     →  Pure Python two-phase algorithm, no C extension needed
 🧭  Step-by-step guide  →  Each move shown with an updated cube net after every step
 📚  Move library        →  Visual diagrams for all 18 standard moves (R U F + inverses)
```

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | React 18, TypeScript, Tailwind CSS, Framer Motion | UI, animations, routing |
| **Backend** | Python 3.9+, FastAPI, Uvicorn | REST API server |
| **Solver** | Kociemba (pure Python + precomputed pruning tables) | Two-phase optimal solving |
| **Vision** | OpenCV | HSV color analysis + face contour detection |

---

## Project Structure

```
CubeQ/
│
├── frontend/                         # React SPA
│   └── src/
│       ├── components/
│       │   ├── HeroSection.tsx       # Cinematic landing page with video background
│       │   ├── ScanPage.tsx          # Camera capture + manual sticker input
│       │   ├── SolveGuidePage.tsx    # Step-by-step move walkthrough
│       │   ├── MovesPage.tsx         # Interactive 18-move learning guide
│       │   └── StaggeredFade.tsx     # Character-by-character text animation
│       ├── api/cube.ts               # Typed API client
│       └── App.tsx                   # Route definitions
│
├── backend/                          # FastAPI server
│   ├── main.py                       # App entry point
│   ├── api/routes.py                 # All REST endpoints
│   ├── core/
│   │   ├── cube.py                   # Cube state model + all 18 move implementations
│   │   ├── solver.py                 # Kociemba solver integration
│   │   └── validator.py              # State validity + parity checks
│   ├── vision/
│   │   └── scanner.py                # Face detection + color classification
│   └── kociemba/                     # Pure Python two-phase algorithm
│       ├── search.py                 # IDA* search (phase 1 + phase 2)
│       ├── facecube.py               # Facelet representation
│       ├── cubiecube.py              # Cubie representation + move tables
│       ├── coordcube.py              # Coordinate representation
│       └── prunetables/              # Precomputed pruning tables (.pkl)
│
└── public/
    └── cube.mp4                      # Hero section background video
```

---

## Getting Started

### Prerequisites

- Python **3.9+**
- Node.js **18+**

### 1 — Clone the repo

```bash
git clone https://github.com/Mmanas-tech/CubeQ.git
cd CubeQ
```

### 2 — Start the backend

```bash
cd backend

# Set up virtual environment
python -m venv .venv

.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS / Linux

# Install dependencies
pip install fastapi uvicorn opencv-python numpy

# Run the server
python -m uvicorn main:app --reload --port 8000
```

Backend running at → `http://localhost:8000`

### 3 — Start the frontend

```bash
cd frontend

npm install
npm run dev
```

App running at → [`http://localhost:5173`](http://localhost:5173)

> The Vite dev server proxies all `/api` requests to `localhost:8000` automatically.

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/solved` | Returns a solved cube state |
| `POST` | `/api/validate` | Validates a cube state for correctness |
| `POST` | `/api/solve` | Solves a cube — accepts `state` + optional `timeout` |
| `POST` | `/api/scramble` | Generates a random scrambled state |
| `POST` | `/api/apply-move` | Applies a move sequence to a given state |
| `POST` | `/api/scan-face` | Scans a face from an uploaded image |
| `POST` | `/api/manual-face` | Sets face colors manually |

---

## Cube Reference

### Orientation

Hold your cube with **White facing up** and **Green facing toward you:**

```
              ┌─────────┐
              │  U (W)  │
         ┌────┼─────────┼────┬─────────┐
         │ L  │  F (G)  │ R  │  B (Bl) │
         │(O) │         │(R) │         │
         └────┼─────────┼────┴─────────┘
              │  D (Y)  │
              └─────────┘
```

**Scanning order:** `White → Yellow → Red → Green → Blue → Orange`

### State Format

```json
{
  "U": ["W","W","W","W","W","W","W","W","W"],
  "R": ["R","R","R","R","R","R","R","R","R"],
  "F": ["G","G","G","G","G","G","G","G","G"],
  "D": ["Y","Y","Y","Y","Y","Y","Y","Y","Y"],
  "L": ["O","O","O","O","O","O","O","O","O"],
  "B": ["B","B","B","B","B","B","B","B","B"]
}
```

`W` White · `Y` Yellow · `R` Red · `O` Orange · `G` Green · `B` Blue

### Move Notation

| Move | Face | CW | CCW | 180° |
|---|---|---|---|---|
| R | Right | `R` | `R'` | `R2` |
| L | Left | `L` | `L'` | `L2` |
| U | Up | `U` | `U'` | `U2` |
| D | Down | `D` | `D'` | `D2` |
| F | Front | `F` | `F'` | `F2` |
| B | Back | `B` | `B'` | `B2` |

All 18 moves are shown with visual diagrams in the **Moves** page of the app.

---

## How the Solver Works

CubeIQ implements **Kociemba's two-phase algorithm** in pure Python:

**Phase 1** reduces the cube to the `〈U, D, R2, L2, F2, B2〉` subgroup — solving edge orientation, corner orientation, and E-slice edge permutation simultaneously using IDA* search with precomputed pruning tables.

**Phase 2** solves within that subgroup to reach the fully solved state, again with IDA* and a separate set of pruning tables.

Solutions average **18–25 moves** and compute in **1–15 seconds** depending on scramble depth.

---

## Known Limitations

| Limitation | Workaround |
|---|---|
| Lighting sensitivity — harsh shadows or direct sunlight can confuse HSV detection | Use diffuse indoor lighting; tap to correct misdetected stickers |
| Glossy stickers — reflections skew color readings | Use the manual sticker input fallback |
| Solve time — deeply scrambled cubes can take up to 15s | Pass a `timeout` param to `/api/solve` for faster (slightly longer) solutions |

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

<div align="center">

<br />

Built by [Manas](https://github.com/Mmanas-tech)

<br />

</div>
