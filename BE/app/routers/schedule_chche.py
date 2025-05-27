from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
import re,json
from app.database import get_db
from app.models.jeju_cafe import JejuCafe
from app.models.jeju_restaurant import JejuRestaurant
from app.models.jeju_tourism import JejuTourism
from app.models.jeju_hotel import JejuHotel
from app.models.jeju_transport import JejuTransport
from app.cache import user_schedules
from app.schemas import (
    ScheduleInitInput, ScheduleInitOutput, UserPreference,
    NewScheduleInput
)
from TripScheduler.tripscheduler.scheduler_api import schedule_trip

router = APIRouter(prefix="/api/users/schedules", tags=["Schedule"])

PLACE_MODELS = {
    "cafe": JejuCafe,
    "restaurant": JejuRestaurant,
    "landmark": JejuTourism,
    "accommodation": JejuHotel,
    "transport": JejuTransport
}

CATEGORY_KEYWORD_MAPPING = {
    "accommodation": [
        "숙박", "호텔", "모텔", "리조트", "리조트부속건물", "펜션", "펜션부속시설",
        "게스트하우스", "민박", "전통숙소", "생활형숙박시설", "쉐어하우스", "레지던스",
        "여관", "원룸"
        ],
    "restaurant": [
        "음식점", "가정식", "갈비탕", "감자탕", "게요리", "고기요리", "곰탕", "곱창", "국밥", "국수",
        "김밥", "꼬치", "낙지요리", "닭갈비", "닭강정", "닭발", "닭볶음탕", "닭요리", "덮밥", "도넛",
        "도시락", "돈가스", "돼지고기구이", "두부요리", "라면", "마라탕", "막국수", "만두", "매운탕",
        "백숙", "보리밥", "보쌈", "복어요리", "분식", "불닭", "뷔페", "브런치", "브런치카페", "비빔밥",
        "생선구이", "생선요리", "생선회", "샌드위치", "샐러드", "샐러드뷔페", "샤브샤브", "소고기구이",
        "소바", "순대", "술집", "스테이크", "스파게티", "아귀찜", "아이스크림", "양갈비", "양꼬치",
        "양식", "오니기리", "오리요리", "오징어요리", "요리주점", "이자카야", "이탈리아음식", "일식당",
        "일품순두부", "전", "전골", "전복요리", "주꾸미요리", "죽", "중식당", "중식만두", "찐빵", "찜닭",
        "케이크전문", "토스트", "포장마차", "푸드코트", "푸드트럭", "퓨전음식", "핫도그", "해장국",
        "햄버거", "향토음식", "호떡"
        ],
    "landmark": [
        "산", "계곡", "해변", "폭포", "섬", "호수", "동굴", "숲", "평야", "저수지",
        "자연", "자연명소", "자연공원", "봉우리", "명소", "유적", "유적지", "사찰",
        "성곽명", "기념관", "기념물", "문화", "문화시설", "문화원", "박물관", "미술관",
        "기념품", "전시관", "홍보관", "체험", "체험여행", "체험마을", "관광농원",
        "관광안내소", "관광민예품", "관광선", "유원지", "테마공원", "테마파크", "놀이기구",
        "워터파크", "눈썰매장", "레일바이크", "ATV체험장", "승마장", "스킨스쿠버", "서핑",
        "실내놀이터", "실내서핑", "캠핑", "해양레저", "항공레저", "짚라인", "드라이브",
        "레저", "레포츠시설", "요트", "잠수함", "배낚시", "전망대", "일출명소", "등산코스",
        "산책로", "수목원", "근린공원", "공원", "등대", "오름", "항구", "선착장",
        "도보코스", "명상", "템플스테이"
        ],
    "transport": ["transport"]
}

WEEKDAYS_KO = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]

# 카테고리 매핑
def get_mapped_category(category: str) -> str | None:
    if not category:
        return None
    category = category.strip()
    for mapped, keywords in CATEGORY_KEYWORD_MAPPING.items():
        for keyword in keywords:
            if keyword in category:
                return mapped
    return None

# DB 조회
def enrich_places_with_db(places, db):
    enriched = []
    for place in places:
        for category, PlaceModel in PLACE_MODELS.items():
            db_place = db.query(PlaceModel).filter(
                func.trim(func.lower(PlaceModel.name)) == func.trim(func.lower(place.name))
            ).first()
            if db_place:
                enriched.append({
                    "name": db_place.name,
                    "x_cord": float(db_place.x_cord),
                    "y_cord": float(db_place.y_cord),
                    "category": category
                })
                break
    return enriched

# user 디폴드값
def build_user_preference(input_data: ScheduleInitInput) -> UserPreference:
    default_user = {
        "start_time": "09:00",
        "end_time": "21:00",
        "travel_style": "relaxed",
        "meal_time_preferences": {
            "breakfast": ["08:00", "09:00"],
            "lunch": ["12:00", "13:00"],
            "dinner": ["18:00", "19:00"]
        }
    }
    user_data = input_data.user.dict() if input_data.user else {}
    for key, value in default_user.items():
        if key not in user_data or not user_data[key]:
            user_data[key] = value
    for meal in ["breakfast", "lunch", "dinner"]:
        if meal not in user_data["meal_time_preferences"] or not user_data["meal_time_preferences"][meal]:
            user_data["meal_time_preferences"][meal] = default_user["meal_time_preferences"][meal]
    return UserPreference(**user_data)

# ------------------- /init -------------------
@router.post("/init", response_model=ScheduleInitOutput)
def init_schedule(input_data: ScheduleInitInput, db: Session = Depends(get_db)):
    user_id = input_data.date.user_id
    user_preference = build_user_preference(input_data)

    user_schedules[user_id] = {
        "date": input_data.date,
        "user": user_preference,
        "places_by_day": {}
    }

    start_dt = datetime.strptime(input_data.date.start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(input_data.date.end_date, "%Y-%m-%d")
    day_count = (end_dt - start_dt).days + 1

    enriched_places_by_day = {}
    for i in range(day_count):
        day_index = i + 1
        places = input_data.places_by_day.get(day_index, [])
        enriched_places = enrich_places_with_db(places, db)
        enriched_places_by_day[day_index] = enriched_places

    user_schedules[user_id]["places_by_day"] = enriched_places_by_day
    return ScheduleInitOutput(places_by_day=enriched_places_by_day)

def clean_place_name(name: str) -> str:
    return name.split("(")[0].strip()

def strip_suffix_tags(name: str) -> str:
    return re.sub(r"\s*\([^)]*\)", "", name).strip()

# 경로최적화 결과 출력 
def format_schedule_output(input_data: NewScheduleInput, result: dict, db: Session) -> dict:
    visits = result["visits"]
    path = result["path"]
    day = next(iter(input_data.places_by_day))
    input_places = input_data.places_by_day[day]

    formatted_places = []
    for visit in sorted(visits, key=lambda x: x["order"]):
        original_name = visit["place"]
        cleaned_name = clean_place_name(original_name)
        display_name = strip_suffix_tags(original_name)

        db_place = None
        for model in PLACE_MODELS.values():
            db_place = db.query(model).filter(
                func.trim(func.lower(model.name)) == func.trim(func.lower(cleaned_name))
            ).first()
            if db_place:
                break

        address = getattr(db_place, "address", "unknown") if db_place else "unknown"

        formatted_places.append({
            "name": display_name,
            "address": address,
            "arrival_str": visit["arrival_str"],
            "departure_str": visit["departure_str"],
            "service_time": visit["stay_duration"],
            "x_cord": visit["x_cord"],
            "y_cord": visit["y_cord"]
        })

    return {
        "places_by_day": {day: formatted_places},
        "path": path
    }

# 경로 최적화 input
def enrich_input_places(places_input, db: Session):
    enriched_places = []
    for place in places_input:
        db_place = None
        matched_category = None

        # Step 1: 일반 탐색
        for category, PlaceModel in PLACE_MODELS.items():
            candidate = db.query(PlaceModel).filter(
                func.trim(func.lower(PlaceModel.name)) == func.trim(func.lower(place.name))
            ).first()
            if candidate:
                db_place = candidate
                matched_category = category
                print(f"✅ [직접매칭] {place.name} → category: {matched_category}")
                break

        # Step 2: 카테고리 매핑 사용
        if not db_place and hasattr(place, "category"):
            mapped = get_mapped_category(place.category)
            if mapped and mapped in PLACE_MODELS:
                Model = PLACE_MODELS[mapped]
                db_place = db.query(Model).filter(
                    func.trim(func.lower(Model.name)) == func.trim(func.lower(place.name))
                ).first()
                matched_category = mapped
                print(f"✅ [카테고리매핑] {place.name} → category: {matched_category}")
            else:
                print(f"⚠️ [카테고리매핑실패] {place.name} → category 원본: {place.category} → 매핑 실패")
        if not db_place:
            print(f"❌ [DB조회실패] {place.name} → 어떤 테이블에서도 찾지 못함")

        if db_place:
            open_time = db_place.open_time or "00:00"
            close_time = "23:59" if db_place.close_time == "24:00" else (db_place.close_time or "23:59")
            enriched_places.append({
                "id": db_place.id,
                "name": db_place.name,
                "x_cord": float(db_place.x_cord),
                "y_cord": float(db_place.y_cord),
                "category": matched_category,
                "open_time": open_time,
                "close_time": close_time,
                "service_time": getattr(place, "service_time", None) or 30,
                "tags": [],
                "closed_days": [],
                "break_time": [],
                "is_mandatory": False
            })
    return enriched_places

# ------------------- /schedule -------------------
@router.post("/schedule")
def generate_schedule(input_data: NewScheduleInput, db: Session = Depends(get_db)):
    user_id = input_data.user_id
    if user_id not in user_schedules:
        raise HTTPException(status_code=404, detail="일정을 먼저 초기화해야 합니다.")

    user_data = user_schedules[user_id]
    start_date = datetime.strptime(user_data["date"].start_date, "%Y-%m-%d")
    end_date = datetime.strptime(user_data["date"].end_date, "%Y-%m-%d")
    total_days = (end_date - start_date).days + 1

    i = int(next(iter(input_data.places_by_day.keys())))
    places_input = input_data.places_by_day.get(i, [])
    enriched_places = enrich_input_places(places_input, db)

    current_date = start_date + timedelta(days=i - 1)
    day_info_dict = {
        "is_first_day": (i == 1),
        "is_last_day": (i == total_days),
        "date": current_date.strftime("%Y-%m-%d"),
        "weekday": WEEKDAYS_KO[current_date.weekday()]
    }

    input_dict = {
        "places": enriched_places,
        "user": user_data["user"].dict(),
        "day_info": day_info_dict
    }

    print("📦 알고리즘 input_dict ↓↓↓")
    print(json.dumps(input_dict, ensure_ascii=False, indent=2))
    result = schedule_trip(input_dict)

    print("✅ 최종 포함된 장소 목록:")
    for v in result["visits"]:
        print(f"- {v['place']} (도착: {v['arrival_str']}, 소요: {v['stay_duration']})")

    return format_schedule_output(input_data, result, db)