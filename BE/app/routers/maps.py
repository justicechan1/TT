from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Dict, Tuple
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
from ._utils import to_float, cos_sim, avg_vec

router = APIRouter(prefix="/api/users/maps", tags=["maps"])

# 카테고리 표기(한글/영문/대소문자) 정규화
CATEGORY_ALIAS: Dict[str, str] = {
    "cafe": "cafe", "카페": "cafe", "Cafe": "cafe", "CAFE": "cafe",
    "hotel": "hotel", "숙소": "hotel", "Hotel": "hotel", "HOTEL": "hotel",
    "restaurant": "restaurant", "음식점": "restaurant",
    "Restaurant": "restaurant", "RESTAURANT": "restaurant",
    "tour": "tour", "관광지": "tour", "Tour": "tour", "TOUR": "tour",
}

def _norm_cat(c: str) -> str:
    return CATEGORY_ALIAS.get(c, c).lower()

# JOIN_INFO: (PlaceModel, MapModel, fk_on_map, pk_on_place, x_col, y_col)
JOIN_INFO: Dict[str, Tuple] = {
    "cafe": (
        JejuCafe,
        CafeHashtagMap,
        CafeHashtagMap.cafe_id,     # fk: map.cafe_id
        JejuCafe.cafe_id,           # pk: cafe.cafe_id
        JejuCafe.x_cord,
        JejuCafe.y_cord,
    ),
    "hotel": (
        JejuHotel,
        HotelHashtagMap,
        HotelHashtagMap.hotel_id,
        JejuHotel.hotel_id,
        JejuHotel.x_cord,
        JejuHotel.y_cord,
    ),
    "restaurant": (
        JejuRestaurant,
        RestaurantHashtagMap,
        RestaurantHashtagMap.restaurant_id,
        JejuRestaurant.restaurant_id,
        JejuRestaurant.x_cord,
        JejuRestaurant.y_cord,
    ),
    "tour": (
        JejuTour,
        TourHashtagMap,
        TourHashtagMap.tour_id,
        JejuTour.tour_id,
        JejuTour.x_cord,
        JejuTour.y_cord,
    ),
}

def _viewport_filter(x_col, y_col, vp):
    # 좌표가 문자열로 들어와도 안전하게 float 비교
    min_x = to_float(vp.min_x)
    max_x = to_float(vp.max_x)
    min_y = to_float(vp.min_y)
    max_y = to_float(vp.max_y)
    return and_(
        x_col >= min_x, x_col <= max_x,
        y_col >= min_y, y_col <= max_y
    )

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

@router.post("/select_hashtage", response_model=SelectHashtageOut)
def select_hashtage(req: SelectHashtageIn, db: Session = Depends(get_db)):
    """
    선택 해시태그들의 임베딩 평균 → 후보 장소(같은 카테고리)의 해시태그 임베딩 평균과 코사인 유사도
    """
    cat = _norm_cat(req.category)
    if cat not in JOIN_INFO or not req.tag:
        return SelectHashtageOut(select_hashtage=[])

    Place, Map, fk_on_map, pk_on_place, x_c, y_c = JOIN_INFO[cat]

    # 1) 선택 태그 임베딩 평균
    sel_tags = [t.hashtag for t in req.tag]
    tag_rows = (
        db.query(Hashtag)
        .filter(func.lower(Hashtag.hashtag).in_([t.lower() for t in sel_tags]))
        .all()
    )
    sel_vec = avg_vec([list(h.embeddings or []) for h in tag_rows])
    if not sel_vec:
        return SelectHashtageOut(select_hashtage=[])

    # 2) 후보 장소 추출(뷰포트 내)
    places = (
        db.query(Place)
        .filter(_viewport_filter(x_c, y_c, req.viewport))
        .limit(2000)
        .all()
    )

    # 3) 각 장소의 태그 임베딩 평균 → 코사인 유사도
    results = []
    for p in places:
        pid = getattr(p, pk_on_place.key)  

        tag_rows = (
            db.query(Hashtag.embeddings, Hashtag.hashtag)
            .join(Map, Map.hashtag_id == Hashtag.hashtag_id)
            .filter(fk_on_map == pid)     
            .all()
        )
        place_vec = avg_vec([list(e or []) for (e, _) in tag_rows])
        sim = cos_sim(sel_vec, place_vec) if place_vec else 0.0

        results.append(SelectHashtageOutItem(
            name=getattr(p, "name", ""),      
            category=cat,
            x_cord=to_float(p.x_cord) or 0.0,
            y_cord=to_float(p.y_cord) or 0.0,
            similarity=float(sim)
        ))

    results.sort(key=lambda x: x.similarity, reverse=True)
    return SelectHashtageOut(select_hashtage=results[:100])
