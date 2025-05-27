# router/maps.py

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
import re
from typing import List
from app.cache import selected_category_cache
from app.database import get_db
import json 
import numpy as np
from app.models.jeju_cafe import JejuCafe, JejuCafeHashtag
from app.models.jeju_restaurant import JejuRestaurant, JejurestaurantHashtag
from app.models.jeju_tourism import JejuTourism, JejutourismHashtag
from app.models.jeju_hotel import JejuHotel, JejuhotelHashtag
from app.models.jeju_transport import JejuTransport
from app.schemas.maps import (
    HashtagInput, HashtagOutput, TagInfo,
    MoveInput, MoveResponse, MoveInfo,
    Viewport
)
from app.core.search import search_similar_places

router = APIRouter(prefix="/api/users/maps", tags=["maps"])

PLACE_MODELS = {
    "cafe": (JejuCafe, JejuCafeHashtag),
    "restaurant": (JejuRestaurant, JejurestaurantHashtag),
    "tourist": (JejuTourism, JejutourismHashtag),
    "accommodation": (JejuHotel, JejuhotelHashtag),
    "transport": (JejuTransport, None)
}

PRIMARY_KEY_FIELDS = {
    "cafe": "cafe_id",
    "restaurant": "restaurant_id",
    "tourist": "tour_id",
    "accommodation": "hotel_id"
}

# ---------- /hashtage ----------
@router.post("/hashtage", response_model=HashtagOutput)
def get_hashtags(input_data: HashtagInput, db: Session = Depends(get_db)):
    category = input_data.category.lower()
    viewport = input_data.viewport

    if category not in PLACE_MODELS:
        raise HTTPException(status_code=400, detail="Invalid category")

    # 카테고리 캐시 저장
    selected_category_cache["current"] = category

    PlaceModel, HashtagModel = PLACE_MODELS[category]
    pk_field = getattr(PlaceModel, PRIMARY_KEY_FIELDS[category])
    fk_field = getattr(HashtagModel, PRIMARY_KEY_FIELDS[category])

    subquery = db.query(pk_field).filter(
        PlaceModel.x_cord.between(viewport.min_x, viewport.max_x),
        PlaceModel.y_cord.between(viewport.min_y, viewport.max_y)
    ).subquery()

    hashtag_rows = db.query(HashtagModel.hashtag).filter(
        fk_field.in_(subquery),
        HashtagModel.hashtag.isnot(None)
    ).all()

    unique_tags = set()
    for row in hashtag_rows:
        if not row.hashtag:
            continue
        try:
            tags = re.findall(r'#\w+', row.hashtag)
            unique_tags.update(tags)
        except Exception as e:
            print(f"❌ 해시태그 파싱 실패: {e}")

    return HashtagOutput(tag=[TagInfo(hashtag=tag) for tag in unique_tags])

# ---------- Viewport 내 장소 조회 ----------
def get_places_in_viewport(category: str, viewport: Viewport, db: Session) -> List[MoveInfo]:
    if category not in PLACE_MODELS:
        raise HTTPException(status_code=400, detail="Invalid category")

    PlaceModel, _ = PLACE_MODELS[category]

    places = db.query(PlaceModel).filter(
        PlaceModel.x_cord.between(viewport.min_x, viewport.max_x),
        PlaceModel.y_cord.between(viewport.min_y, viewport.max_y)
    ).all()

    results = []
    for place in places:
        results.append(MoveInfo(
            name=place.name,
            x_cord=float(place.x_cord),
            y_cord=float(place.y_cord)
        ))

    return results

# ---------- 장소별 해시태그 임베딩 수집 ----------
def collect_place_embeddings(db, PlaceModel, HashtagModel, pk_field_name, viewport):
    places = db.query(PlaceModel).filter(
        PlaceModel.x_cord.between(viewport.min_x, viewport.max_x),
        PlaceModel.y_cord.between(viewport.min_y, viewport.max_y)
    ).all()

    embedding_logs = []
    for place in places:
        place_id = getattr(place, pk_field_name)
        if HashtagModel:
            rows = db.query(HashtagModel.embeddings).filter(
                getattr(HashtagModel, pk_field_name) == place_id,
                HashtagModel.embeddings.isnot(None)
            ).all()
            emb_list = []
            for e in rows:
                try:
                    parsed = json.loads(e[0])  # 🔥 문자열 → 리스트
                    emb_list.append(np.array(parsed, dtype=np.float32).reshape(1, -1))
                except Exception as err:
                    print(f"[❌ 임베딩 파싱 오류] {e[0]} → {err}")
            if emb_list:
                embedding_logs.append({
                    "id": place_id,
                    "embedding": np.vstack(emb_list)
                })
    return embedding_logs

# ---------- 선택된 해시태그 벡터 수집 ----------
def collect_selected_embeddings(db, HashtagModel, tags, seen_embeddings: set):
    selected = []
    for tag in tags:
        rows = db.query(HashtagModel.hashtag, HashtagModel.embeddings).filter(
            HashtagModel.hashtag.like(f"%{tag}%")
        ).all()
        for name, embedding in rows:
            if embedding is None:
                continue
            try:
                key = embedding.strip()
                if key in seen_embeddings:
                    continue
                seen_embeddings.add(key)
                parsed = json.loads(embedding)  # 🔥 문자열 → 리스트
                selected.append(np.array(parsed, dtype=np.float32).reshape(1, -1))
            except Exception as err:
                print(f"[❌ 선택 해시태그 임베딩 파싱 실패] {embedding} → {err}")
    return selected


# ---------- 유사도 기반 상위 장소 ID 추출 ----------
def get_top_place_ids(selected_embeddings, embedding_logs):
    top_ids = set()
    for query_vector in selected_embeddings:
        top_results = search_similar_places(query_vector.T, embedding_logs, top_k=5)
        for res in top_results:
            top_ids.add(res["place_id"])
    return top_ids

# ---------- 최종 MoveInfo 응답 생성 ----------
def build_filtered_move_response_with_similarity(db, PlaceModel, pk_field_name, top_results):
    move_infos = []
    for res in top_results:
        pid = res["place_id"]
        similarity = res["similarity"]
        db_place = db.query(PlaceModel).filter(getattr(PlaceModel, pk_field_name) == pid).first()
        if db_place:
            move_infos.append({
                "name": db_place.name,
                "x_cord": float(db_place.x_cord),
                "y_cord": float(db_place.y_cord),
                "similarity": similarity
            })
    return move_infos

# ---------- /select_hashtage ----------
@router.post("/select_hashtage", response_model=MoveResponse)
def get_move_candidates(input_data: MoveInput, db: Session = Depends(get_db)):
    viewport = input_data.viewport
    tags = [t.hashtag for t in input_data.tag]
    category = input_data.category.lower()

    if category not in PLACE_MODELS:
        raise HTTPException(status_code=400, detail="Invalid category")
    
    selected_category_cache["current"] = category

    PlaceModel, HashtagModel = PLACE_MODELS[category]
    pk_field_name = PRIMARY_KEY_FIELDS[category]

    embedding_logs = collect_place_embeddings(db, PlaceModel, HashtagModel, pk_field_name, viewport)
    selected_embeddings = collect_selected_embeddings(db, HashtagModel, tags, seen_embeddings=set())

    all_top_results = []
    for query_vector in selected_embeddings:
        all_top_results.extend(search_similar_places(query_vector.T, embedding_logs, top_k=5))

    # 중복제거후 유사도 높은 순으로
    unique_results = {res["place_id"]: res for res in sorted(all_top_results, key=lambda x: x["similarity"], reverse=True)}
    filtered_places = build_filtered_move_response_with_similarity(db, PlaceModel, pk_field_name, list(unique_results.values()))

    return MoveResponse(select_hashtage=filtered_places)
