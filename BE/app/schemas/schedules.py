from typing import Dict, List, Optional
from pydantic import BaseModel, Field


# ---------- /api/users/schedules /init ----------
# Input
class DateIn(BaseModel):
    user_id: str
    start_date: str
    end_date: str
    arrival_time: str
    departure_time: str

class UserPrefIn(BaseModel):
    start_time: str
    end_time: str
    travel_style: str
    meal_time_preferences: Dict[str, List[str]] 

class PlaceNameIn(BaseModel):
    name: str

class InitRequest(BaseModel):
    date: DateIn
    user: UserPrefIn
    places_by_day: Dict[int, List[PlaceNameIn]]

# Output
class PlaceOutLite(BaseModel):
    name: str
    x_cord: float
    y_cord: float
    category: str

class InitResponse(BaseModel):
    places_by_day: Dict[int, List[PlaceOutLite]]

    class Config:
        from_attributes = True


# ---------- /api/users/schedules /schedul ----------
# Input (명세는 GET+Body 구조지만, 스키마는 그대로 둠)
class PlaceWithServiceIn(BaseModel):
    name: str
    service_time: int

class SchedulRequest(BaseModel):
    user_id: str
    places_by_day: Dict[int, List[PlaceWithServiceIn]]

# Output
class PlaceWithTimingOut(BaseModel):
    name: str
    category: str
    address: str
    arrival_str: str
    departure_str: str
    service_time: int
    x_cord: float
    y_cord: float

class SchedulResponse(BaseModel):
    places_by_day: Dict[int, List[PlaceWithTimingOut]]
    path: List[List[List[float]]]  # [[[x,y], [x,y]], ...]

    class Config:
        from_attributes = True


# ---------- /api/users/schedules /itinerary ----------
# Input
class PlaceItineraryIn(BaseModel):
    name: str
    arrival_str: str
    departure_str: str
    service_time: int

class ItineraryRequest(BaseModel):
    places_by_day: Dict[int, List[PlaceItineraryIn]]

# Output
class PlaceItineraryOut(BaseModel):
    name: str
    address: str
    category: str
    open_time: str = ""
    close_time: str = ""
    convenience: List[str]
    arrival_str: str
    departure_str: str
    service_time: int
    description: str
    image_urls: List[str]

class ItineraryResponse(BaseModel):
    places_by_day: Dict[int, List[PlaceItineraryOut]]

    class Config:
        from_attributes = True
