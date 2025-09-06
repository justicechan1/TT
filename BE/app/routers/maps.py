from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Dict, Tuple, List
import numpy as np

from app.database import get_db

from app.models.hashtag import Hashtag
from app.models.hashtag_mapping import (
    CafeHashtagMap, HotelHashtagMap, RestaurantHashtagMap, TourHashtagMap
)
from app.models.jeju_cafe import JejuCafe
from app.models.jeju_hotel import JejuHotel
from app.models.jeju_restaurant import JejuRestaurant
from app.models.jeju_tour import JejuTour

from app.schemas.maps import (
    HashtageIn, HashtageOut, HashtagOnly,
    SelectHashtageIn, SelectHashtageOut, SelectHashtageOutItem
)
from ._utils import to_float, avg_vec, normalize_vectors  # ← 여기로 단일화

router = APIRouter(prefix="/api/users/maps", tags=["maps"])

# 카테고리 표기 정규화(한글/영문/대소문자)
CATEGORY_ALIAS: Dict[str, str] = {
    "cafe": "cafe", "카페": "cafe", "Cafe": "cafe", "CAFE": "cafe",
    "hotel": "hotel", "숙소": "hotel", "Hotel": "hotel", "HOTEL": "hotel",
    "restaurant": "restaurant", "음식점": "restaurant",
    "Restaurant": "restaurant", "RESTAURANT": "restaurant",
    "tour": "tour", "관광지": "tour", "Tour": "tour", "TOUR": "tour",
}
def _norm_cat(c: str) -> str:
    return CATEGORY_ALIAS.get(c, c).lower()

# (PlaceModel, MapModel, fk_on_map, pk_on_place, x_col, y_col)
JOIN_INFO: Dict[str, Tuple] = {
    "cafe":       (JejuCafe,       CafeHashtagMap,       CafeHashtagMap.cafe_id,       JejuCafe.cafe_id,       JejuCafe.x_cord,       JejuCafe.y_cord),
    "hotel":      (JejuHotel,      HotelHashtagMap,      HotelHashtagMap.hotel_id,     JejuHotel.hotel_id,     JejuHotel.x_cord,      JejuHotel.y_cord),
    "restaurant": (JejuRestaurant, RestaurantHashtagMap, RestaurantHashtagMap.restaurant_id, JejuRestaurant.restaurant_id, JejuRestaurant.x_cord, JejuRestaurant.y_cord),
    "tour":       (JejuTour,       TourHashtagMap,       TourHashtagMap.tour_id,       JejuTour.tour_id,       JejuTour.x_cord,       JejuTour.y_cord),
}

def _viewport_filter(x_col, y_col, vp):
    min_x = to_float(vp.min_x); max_x = to_float(vp.max_x)
    min_y = to_float(vp.min_y); max_y = to_float(vp.max_y)
    return and_(x_col >= min_x, x_col <= max_x, y_col >= min_y, y_col <= max_y)

@router.post("/hashtage", response_model=HashtageOut)
def hashtage(req: HashtageIn, db: Session = Depends(get_db)):
    cat = _norm_cat(req.category)
    if cat not in JOIN_INFO:
        return HashtageOut(tag=[])

    Place, Map, fk_on_map, pk_on_place, x_c, y_c = JOIN_INFO[cat]

    rows = (
        db.query(Hashtag.hashtag, func.count().label("cnt"))
        .join(Map, Map.hashtag_id == Hashtag.hashtag_id)
        .join(Place, fk_on_map == pk_on_place)               
        .filter(_viewport_filter(x_c, y_c, req.viewport))
        .group_by(Hashtag.hashtag)
        .order_by(func.count().desc())
        .all()
    )
    return HashtageOut(tag=[HashtagOnly(hashtag=h) for (h, _) in rows])

#@router.post("/select_hashtag", response_model=SelectHashtageOut)
