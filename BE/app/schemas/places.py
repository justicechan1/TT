#schemas/places.py
from pydantic import BaseModel
from typing import List, Optional, Dict


# ------------------- /api/places/edit -------------------
class PlaceNameOnly(BaseModel):
    name: str

class PlaceSearchRequest(BaseModel):
    name: str
    
class PlaceEditInput(BaseModel):
    user_id: str
    places_by_day: Dict[int, List[PlaceNameOnly]]

class PlaceEditOutput(BaseModel):
    places_by_day: Dict[int, List[PlaceNameOnly]]

# ------------------- /api/places/search -------------------
class PlaceSearchResult(BaseModel):
    name: str

class PlaceSearchOutput(BaseModel):
    search: List[PlaceSearchResult]

# ------------------- /api/places/data -------------------
class PlaceDataResult(BaseModel):
    name: str
    address: str
    x_cord: Optional[float] = None
    y_cord: Optional[float] = None
    open_time: Optional[str] = None
    close_time: Optional[str] = None
    convenience: Optional[str] = None
    image_urls: List[str] = []

    class Config:
        from_attributes = True

class PlaceDataResponse(BaseModel):
    places: PlaceDataResult