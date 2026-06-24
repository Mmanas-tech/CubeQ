# CubeIQ

> Scan a scrambled Rubik's Cube with your camera. Get the solution in under 15 seconds.

CubeIQ uses OpenCV to detect cube face colors from a live camera feed, validates the state, and runs Kociemba's two-phase algorithm to compute a solution — then walks you through every move with a visual, step-by-step guide.

---

## Demo

<!-- Replace with actual screenshot or GIF once available -->
| Scanning | Solution Guide | Move Library |
|---|---|---|
| ![scan](public/screenshots/scan.png) | ![solve](public/screenshots/solve.png) | ![moves](public/screenshots/moves.png) |

---

## Features

- **Camera scanning** — Point your camera at each face; HSV color detection auto-fills sticker colors
- **Manual fallback** — Tap any sticker to cycle its color if the camera misses it
- **Kociemba solver** — Pure Python two-phase algorithm, no C extension required
- **Step-by-step guide** — Every move shown with an updated cube net so you always know what to expect next
- **Move library** — Interactive visual diagrams for all 18 standard moves (R, U, F and their inverses/doubles)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, TypeScript, Tailwind CSS, Framer Motion |
| Backend | Python 3.9+, FastAPI, Uvicorn |
| Solver | Kociemba two-phase algorithm (pure Python, precomputed pruning tables) |
| Vision | OpenCV — HSV analysis + contour-based face detection |

---

## Project Structure

```
CubeQ/
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── HeroSection.tsx       # Landing page with video background
│       │   ├── ScanPage.tsx          # Camera + manual cube scanning
│       │   ├── SolveGuidePage.tsx    # Step-by-step solution display
│       │   ├── MovesPage.tsx         # Interactive moves learning guide
│       │   └── StaggeredFade.tsx     # Character-by-character text animation
│       ├── api/cube.ts               # API client helpers
│       └── App.tsx                   # Routes
│
├── backend/
│   ├── main.py                       # FastAPI entry point
│   ├── api/routes.py                 # REST endpoints
│   ├── core/
│   │   ├── cube.py                   # Cube state model + all 18 move implementations
│   │   ├── solver.py                 # Kociemba solver integration
│   │   └── validator.py              # State validity + parity checks
│   ├── vision/
│   │   └── scanner.py                # OpenCV face detection + color recognition
│   └── kociemba/                     # Pure Python two-phase algorithm
│       ├── search.py                 # IDA* search (phase 1 + phase 2)
│       ├── facecube.py               # Facelet representation
│       ├── cubiecube.py              # Cubie representation + move tables
│       ├── coordcube.py              # Coordinate representation
│       └── prunetables/              # Precomputed pruning tables (.pkl)
│
└── public/
    └── cube.mp4                      # Hero background video
```

---

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 18+

### Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS / Linux

# Install dependencies
pip install fastapi uvicorn opencv-python numpy

# Start server
python -m uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend

npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173). The dev server proxies `/api` requests to `localhost:8000`.

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/solved` | Returns a solved cube state |
| POST | `/api/validate` | Validates a cube state |
| POST | `/api/solve` | Solves a cube — accepts `state` + optional `timeout` |
| POST | `/api/scramble` | Generates a random scrambled state |
| POST | `/api/apply-move` | Applies a move sequence to a state |
| POST | `/api/scan-face` | Scans a face from an uploaded image |
| POST | `/api/manual-face` | Sets face colors manually |

---

## Cube State Format

The cube is a dictionary of 6 faces, each with 9 stickers in row-major order:

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

Color codes: `W` White · `Y` Yellow · `R` Red · `O` Orange · `G` Green · `B` Blue

---

## Cube Orientation

Hold your cube with:
- **White center** facing up
- **Green center** facing toward you

```
             [ U — White ]
[ L — Orange ] [ F — Green ] [ R — Red ] [ B — Blue ]
             [ D — Yellow ]
```

Scanning order: **White → Yellow → Red → Green → Blue → Orange**

---

## How the Solver Works

CubeIQ uses **Kociemba's two-phase algorithm:**

**Phase 1** — Reduces the cube to the `<U, D, R2, L2, F2, B2>` subgroup by solving edge orientation, corner orientation, and E-slice edge permutation.

**Phase 2** — Solves within that subgroup to reach the fully solved state.

Solutions are typically 18–25 moves and compute in 1–15 seconds depending on the scramble depth.

---

## Move Notation

| Move | Face | Direction |
|---|---|---|
| `R` / `R'` / `R2` | Right | CW / CCW / 180° |
| `L` / `L'` / `L2` | Left | CW / CCW / 180° |
| `U` / `U'` / `U2` | Up | CW / CCW / 180° |
| `D` / `D'` / `D2` | Down | CW / CCW / 180° |
| `F` / `F'` / `F2` | Front | CW / CCW / 180° |
| `B` / `B'` / `B2` | Back | CW / CCW / 180° |

Visual diagrams for all 18 moves are available in the **Moves** page of the app.

---

## Known Limitations

- **Lighting sensitivity** — Camera scanning works best under consistent, diffuse indoor lighting. Avoid direct sunlight or harsh shadows on the cube face.
- **Solve time** — Heavily scrambled cubes (20 moves) may take up to 15 seconds to solve. A timeout parameter is available in the `/api/solve` endpoint.
- **Glossy stickers** — Reflective cube stickers can confuse the HSV classifier. Use the manual tap-to-correct fallback in that case.

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

<p align="center">Built by <a href="https://github.com/Mmanas-tech">Manas</a></p>