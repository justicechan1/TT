#schemas\schedule.py
from pydantic import BaseModel, Field
from typing import List, Dict, Optional

# ------------------- /init 요청 -------------------

class DateInfo(BaseModel):
    user_id: str
    start_date: str
    end_date: str
    arrival_time: str
    departure_time: str

class MealTimePreferences(BaseModel):
    breakfast: List[str]
    lunch: List[str]
    dinner: List[str]

class UserPreference(BaseModel):
    start_time: str
    end_time: str
    travel_style: str
    meal_time_preferences: MealTimePreferences

class PlaceSimpleInput(BaseModel):
    name: str

class ScheduleInitInput(BaseModel):
    date: DateInfo
    user: UserPreference
    places_by_day: Dict[int, List[PlaceSimpleInput]]

# ------------------- /init 응답 -------------------

class PlaceShortOutput(BaseModel):
    name: str
    x_cord: float
    y_cord: float
    category: str

class ScheduleInitOutput(BaseModel):
    places_by_day: Dict[int, List[PlaceShortOutput]]


# ------------------- /schedul 요청 -------------------
class PlaceWithServiceTime(BaseModel):
    name: str
    service_time: Optional[int] = None

class NewScheduleInput(BaseModel):
    user_id: str
    places_by_day: Dict[int, List[PlaceWithServiceTime]]

# ------------------- /schedul 응답 -------------------
class MealTimePreferences(BaseModel):
    breakfast: List[str]
    lunch: List[str]
    dinner: List[str]

class UserPreference(BaseModel):
    start_time: str
    end_time: str
    travel_style: str
    meal_time_preferences: MealTimePreferences

class DayInfo(BaseModel):
    is_first_day: bool
    is_last_day: bool
    date: str
    weekday: str

class PlaceResult(BaseModel):
    id: int
    name: str
    x_cord: float
    y_cord: float
    category: str
    open_time: str
    close_time: str
    service_time: int
    tags: List[str]
    closed_days: List[str]
    break_time: List[str]
    is_mandatory: bool

class SchedulePerDayOutput(BaseModel):
    places: List[PlaceResult]
    user: UserPreference
    day_info: DayInfo

# ------------------- /itinerary 요청 -------------------
class PlaceTimeInput(BaseModel):
    name: str = Field(..., description="장소 이름")
    arrival_str: Optional[str] = Field(None, description="도착 시간 문자열")
    departure_str: Optional[str] = Field(None, description="출발 시간 문자열")
    service_time: Optional[int] = Field(None, description="체류 시간(분)")

class PlacesByDayInput(BaseModel):
    # "1": [ ... ], "2": [ ... ] 형태 (키가 str/int 모두 허용)
    places_by_day: Dict[str, List[PlaceTimeInput]]

# ------------------- /itinerary 응답 -------------------
class ItineraryPlaceOut(BaseModel):
    name: str
    address: Optional[str] = None
    category: Optional[str] = None
    arrival_str: Optional[str] = None
    departure_str: Optional[str] = None
    service_time: Optional[int] = None
    description: Optional[str] = None
    image_urls: List[str] = []

class ItineraryOut(BaseModel):
    places_by_day: Dict[str, List[ItineraryPlaceOut]]