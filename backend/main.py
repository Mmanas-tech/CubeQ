from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import cube_router

app = FastAPI(
    title="CubeIQ API",
    description="Rubik's Cube Solver API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cube_router, prefix="/api")


@app.get("/")
def root():
    return {"message": "CubeIQ API", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "ok"}
