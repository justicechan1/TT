from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import Dict, List
from app.database import get_db

# models
from app.models.jeju_cafe import JejuCafe
from app.models.jeju_hotel import JejuHotel
from app.models.jeju_restaurant import JejuRestaurant
from app.models.jeju_tour import JejuTour
from app.models.jeju_transport import JejuTransport

# schemas
from app.schemas.schedules import (
    InitRequest, InitResponse, PlaceOutLite,
    SchedulRequest, SchedulResponse, PlaceWithTimingOut,
    ItineraryRequest, ItineraryResponse, PlaceItineraryOut
)

from ._utils import to_float, parse_image_url

router = APIRouter(prefix="/api/users/schedules", tags=["schedules"])

# division → (Model, id_field)
MODEL_INFO = {
    "cafe":       (JejuCafe, "cafe_id"),
    "hotel":      (JejuHotel, "hotel_id"),
    "restaurant": (JejuRestaurant, "restaurant_id"),
    "tour":       (JejuTour, "tour_id"),
    "transport":  (JejuTransport, "transport_id"),
}

# 이름으로 장소 찾기(여러 테이블 통합)
def _find_place_by_name(db: Session, name: str):
    for div, (Model, _) in MODEL_INFO.items():
        row = db.query(Model).filter(func.lower(Model.name) == func.lower(name.strip())).first()
        if row:
            return div, row
    like = f"%{name.strip()}%"
    for div, (Model, _) in MODEL_INFO.items():
        row = db.query(Model).filter(func.lower(Model.name).like(func.lower(like))).first()
        if row:
            return div, row
    return None, None


@router.post("/init", response_model=InitResponse)
def init(req: InitRequest, db: Session = Depends(get_db)):
    out: Dict[int, List[PlaceOutLite]] = {}
    for day, items in req.places_by_day.items():
        day_list: List[PlaceOutLite] = []
        for it in items:
            div, row = _find_place_by_name(db, it.name)
            if not row:
                # 못 찾으면 skip
                continue
            # 좌표 없는 건 제외
            x = to_float(row.x_cord); y = to_float(row.y_cord)
            if x is None or y is None:
                continue
            day_list.append(PlaceOutLite(
                name=row.name, x_cord=x, y_cord=y, category=div
            ))
        out[int(day)] = day_list
    return InitResponse(places_by_day=out)


@router.get("/schedul", response_model=SchedulResponse)
def schedul(req: SchedulRequest = Body(...), db: Session = Depends(get_db)):
    result_places: Dict[int, List[PlaceWithTimingOut]] = {}
    path: List[List[List[float]]] = []

    for day, items in req.places_by_day.items():
        day_list: List[PlaceWithTimingOut] = []
        for it in items:
            div, row = _find_place_by_name(db, it.name)
            if not row:
                continue
            x = to_float(row.x_cord); y = to_float(row.y_cord)
            if x is None or y is None:
                continue

            day_list.append(PlaceWithTimingOut(
                name=row.name,
                category=div,
                address=row.address or "",
                arrival_str="",
                departure_str="",
                service_time=int(it.service_time),
                x_cord=x,
                y_cord=y
            ))
        result_places[int(day)] = day_list

    return SchedulResponse(places_by_day=result_places, path=path)


@router.post("/itinerary", response_model=ItineraryResponse)
def itinerary(req: ItineraryRequest, db: Session = Depends(get_db)):
    out: Dict[int, List[PlaceItineraryOut]] = {}
    for day, items in req.places_by_day.items():
        day_list: List[PlaceItineraryOut] = []
        for it in items:
            div, row = _find_place_by_name(db, it.name)
            if not row:
                continue
            x = to_float(row.x_cord); y = to_float(row.y_cord)
            imgs = parse_image_url(getattr(row, "image_url", None)) or []

            # description 없는 테이블은 None → 빈 문자열 처리
            desc = getattr(row, "description", None) or ""

            day_list.append(PlaceItineraryOut(
                name=row.name,
                address=row.address or "",
                category=div,
                arrival_str=it.arrival_str,
                departure_str=it.departure_str,
                service_time=it.service_time,
                description=desc,
                image_urls=imgs
            ))
        out[int(day)] = day_list
    return ItineraryResponse(places_by_day=out)
