#router/places.py
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Dict
from sqlalchemy import func
import re
from rapidfuzz import fuzz
from app.database import get_db
from app.models.jeju_cafe import JejuCafe
from app.models.jeju_restaurant import JejuRestaurant
from app.models.jeju_tourism import JejuTourism
from app.models.jeju_hotel import JejuHotel
from app.schemas.places import (
    PlaceSearchOutput, PlaceSearchResult,PlaceNameOnly,
    PlaceDataResponse, PlaceDataResult,
)

router = APIRouter(prefix="/api/places", tags=["places"])

PLACE_MODELS = {
    "cafe": JejuCafe,
    "restaurant": JejuRestaurant,
    "tourism": JejuTourism,
    "hotel": JejuHotel
}

# 이미지 URL 추출 함수
def fetch_image_urls(db: Session, model, name: str) -> list[str]:
    db_place = db.query(model).filter(
        func.trim(func.lower(model.name)) == func.trim(func.lower(name))
    ).first()
    if not db_place or not db_place.image_url:
        return []

    try:
        # ["url1"]["url2"]... 형식에서 URL만 추출
        return re.findall(r'\["(https?://[^"]+)"\]', db_place.image_url)
    except Exception as e:
        print(f"[이미지 파싱 오류]: {e}")
        return []

# 전처리 함수
def clean_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'\s+', '', text)
    text = re.sub(r'[^\w가-힣]', '', text)
    return text

# ---------- /search ----------
@router.get("/search", response_model=PlaceSearchOutput)
def search_places(name: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    search_term = clean_text(name)
    scored_results = []

    for model_type, model in PLACE_MODELS.items():
        try:
            places = db.query(model).all()

            for place in places:
                name_l = clean_text(place.name or "")
                category_l = clean_text(getattr(place, "category", ""))
                address_l = clean_text(getattr(place, "address", ""))

                combined = f"{name_l} {category_l} {address_l}"

                # 다양한 유사도 점수 계산
                score1 = fuzz.partial_ratio(search_term, combined)
                score2 = fuzz.token_sort_ratio(search_term, combined)
                score3 = fuzz.ratio(search_term, combined)

                final_score = max(score1, score2, score3)

                if final_score > 50:
                    scored_results.append((final_score, place.name))

        except Exception as e:
            print(f"[{model_type}] 검색 중 오류 발생: {str(e)}")

    # 점수순 정렬 + 중복 제거
    sorted_unique = []
    seen = set()
    for score, name in sorted(scored_results, key=lambda x: x[0], reverse=True):
        if name not in seen:
            sorted_unique.append(PlaceSearchResult(name=name))
            seen.add(name)

    return PlaceSearchOutput(search=sorted_unique)

# ---------- /select_place ----------
@router.get("/select_place", response_model=PlaceDataResponse)
def get_place_detail(name: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    place_name = name.strip()
    for model_type, model in PLACE_MODELS.items():
        place = db.query(model).filter(model.name == place_name).first()
        if place:
            image_urls = fetch_image_urls(db, model, place_name)
            return PlaceDataResponse(
                places=PlaceDataResult(
                    name=place.name,
                    category=getattr(place, "category", model_type),
                    address=place.address,
                    x_cord=getattr(place, "x_cord", None), 
                    y_cord=getattr(place, "y_cord", None),
                    open_time=getattr(place, "open_time", None),
                    close_time=getattr(place, "close_time", None),
                    convenience=getattr(place, "convenience", None),
                    image_urls=image_urls
                )
            )
    raise HTTPException(status_code=404, detail="해당 장소는 데이터베이스에 존재하지 않습니다.")

# 날짜 변환(Day1~DayN)
def convert_to_day_indices(places_by_day: Dict[int, List], start_date_str: str) -> Dict[int, List[PlaceNameOnly]]:
    result = {}
    for day_index in sorted(places_by_day.keys()):
        result[day_index] = [
            PlaceNameOnly(name=p["name"] if isinstance(p, dict) else p.name)
            for p in places_by_day[day_index]
        ]
    return result