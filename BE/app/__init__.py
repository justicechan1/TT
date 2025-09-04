from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.routers import maps, places, schedules

app.include_router(maps.router, prefix="/api/users/maps")
app.include_router(places.router, prefix="/api/places")
app.include_router(schedules.router, prefix="/api/users/schedules")
