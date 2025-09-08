from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
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
from ._utils import _json_vec, _viewport_filter
from app.core.vector import normalize_vectors
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
    Place, Map, fk_on_map, pk_on_place, x_c, y_c = JOIN_INFO.get(req.category, (None,)*6)
    if Place is None:
        return SelectHashtageOut(select_hashtage=[])

    # 1) 입력 해시태그 임베딩
    tag_str = req.tag[0].hashtag
    tag_row = db.query(Hashtag).filter(Hashtag.hashtag == tag_str).first()
    if not tag_row:
        return SelectHashtageOut(select_hashtage=[])
    q = _json_vec(tag_row.embeddings)
    if q is None:
        return SelectHashtageOut(select_hashtage=[])
    q = q / (np.linalg.norm(q) + 1e-8)

    # 2) 뷰포트 내 후보 장소
    places = db.query(Place).filter(_viewport_filter(x_c, y_c, req.viewport)).all()
    if not places:
        return SelectHashtageOut(select_hashtage=[])

    pk_name = pk_on_place.key if hasattr(pk_on_place, "key") else pk_on_place.name
    place_ids: List[int] = []
    info_by_id: Dict[int, Tuple[str, float, float]] = {}
    for p in places:
        pid = getattr(p, pk_name)
        place_ids.append(pid)
        info_by_id[pid] = (p.name, float(p.x_cord), float(p.y_cord))

    # 3) 매핑 조인
    rows = (
        db.query(fk_on_map.label("pid"), Hashtag.embeddings)
          .select_from(Map)
          .join(Hashtag, Hashtag.hashtag_id == Map.hashtag_id)
          .filter(fk_on_map.in_(place_ids))
          .all()
    )

    place_vecs: Dict[int, List[np.ndarray]] = {}
    for r in rows:
        v = _json_vec(r.embeddings)
        if v is not None:
            place_vecs.setdefault(r.pid, []).append(v)

    if not place_vecs:
        return SelectHashtageOut(select_hashtage=[])

    # 4) 각 장소 유사도 계산 
    result: List[Tuple[int, float]] = []
    for pid, vecs in place_vecs.items():
        E = np.vstack(vecs).astype(np.float32)
        E = normalize_vectors(E, axis=1) 
        sim = float(np.max(E.dot(q)))
        result.append((pid, sim))

    if not result:
        return SelectHashtageOut(select_hashtage=[])

    # 5) Top-5 결과
    result.sort(key=lambda x: x[1], reverse=True)
    top5 = result[:5]

    payload: List[SelectHashtageOutItem] = []
    for pid, sim in top5:
        name, x, y = info_by_id[pid]
        payload.append(
            SelectHashtageOutItem(
                name=name, category=req.category, x_cord=x, y_cord=y, similarity=sim
            )
        )

    return SelectHashtageOut(select_hashtage=payload)