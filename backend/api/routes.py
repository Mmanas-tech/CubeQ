from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional
from core.cube import (
    create_solved, apply_move, apply_moves, is_solved,
    scramble, MOVES, ALL_FACES, state_to_tuple
)
from core.solver import solve
from core.validator import validate_cube

router = APIRouter(tags=["cube"])


class CubeState(BaseModel):
    state: Dict[str, List[str]]


class SolveRequest(BaseModel):
    state: Dict[str, List[str]]
    timeout: float = 30.0


class MoveRequest(BaseModel):
    state: Dict[str, List[str]]
    moves: List[str]


class ScrambleRequest(BaseModel):
    num_moves: int = 20
    seed: Optional[int] = None


@router.get("/solved")
def get_solved():
    return {"state": create_solved()}


@router.post("/validate")
def validate_cube_state(req: CubeState):
    valid, err = validate_cube(req.state)
    return {"valid": valid, "error": err}


@router.post("/solve")
def solve_cube(req: SolveRequest):
    result = solve(req.state, timeout=req.timeout)
    if result['success'] and result['moves']:
        solved_state = apply_moves(req.state, result['moves'])
        result['solved_state'] = solved_state
    elif result['success']:
        result['solved_state'] = req.state
    return result


@router.post("/apply-move")
def apply_single_move(req: MoveRequest):
    if len(req.moves) == 0:
        return {"state": req.state, "moves_applied": []}
    current = req.state
    applied = []
    for m in req.moves:
        if m not in MOVES:
            return JSONResponse(status_code=400, content={"error": f"Invalid move: {m}", "state": current, "moves_applied": applied})
        current = apply_move(current, m)
        applied.append(m)
    return {"state": current, "moves_applied": applied}


@router.post("/scramble")
def scramble_cube(req: ScrambleRequest):
    state, moves = scramble(req.num_moves, req.seed)
    return {"state": state, "moves": moves, "num_moves": len(moves)}


@router.get("/moves")
def list_moves():
    return {"moves": list(MOVES.keys())}


@router.post("/scan-face")
async def scan_face(file: UploadFile = File(...), face: str = "F"):
    if face not in ALL_FACES:
        return JSONResponse(status_code=400, content={"error": f"Invalid face: {face}"})
    try:
        import cv2
        import numpy as np
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if image is None:
            return JSONResponse(status_code=400, content={"error": "Could not decode image"})
        from vision.scanner import scan_single_face
        colors = scan_single_face(image, face)
        if colors is None:
            return JSONResponse(status_code=400, content={"error": "Could not detect cube face"})
        return {"face": face, "colors": colors}
    except ImportError:
        return JSONResponse(status_code=500, content={"error": "OpenCV not available"})


class ManualFaceRequest(BaseModel):
    face: str
    colors: List[str]


@router.post("/manual-face")
def manual_face(req: ManualFaceRequest):
    if req.face not in ALL_FACES:
        return JSONResponse(status_code=400, content={"error": f"Invalid face: {req.face}"})
    if len(req.colors) != 9:
        return JSONResponse(status_code=400, content={"error": "Need exactly 9 colors"})
    valid_colors = {'W', 'Y', 'G', 'B', 'O', 'R'}
    for c in req.colors:
        if c not in valid_colors:
            return JSONResponse(status_code=400, content={"error": f"Invalid color: {c}"})
    return {"face": req.face, "colors": req.colors}


cube_router = router
