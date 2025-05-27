import type { PlaceName, Hashtag, Viewport, PlacesByDay, Category } from './common';

// ─── 장소 관련 타입 ───────────────────────────────────

// 지도 마커용 최소 정보
export interface PlaceMarker {
  name: PlaceName;
  category: string;
  x_cord: number;
  y_cord: number;
}

// 상세 페이지용 모든 정보
export interface PlaceDetail extends PlaceMarker {
  address: string;
  open_time: string;   // ISO 8601 "HH:mm" 권장
  close_time: string;  // ISO 8601 "HH:mm" 권장
  convenience: string;
  image_urls: string[];
}

// 단일 장소 상세 응답 래퍼
export interface PlaceResponse {
  place: PlaceDetail;
}

// ─── 해시태그/카테고리 추천 ────────────────────────────

// 1) 해시태그 → 장소 추천
export interface HashtagToPlaceRequest {
  category: Category; // 카테고리 이름
  tag: Hashtag[];    // 단일 요소라도 배열로
  viewport: Viewport;
}

export interface PlaceRecommendation {
  name: string;
  x_cord: number;
  y_cord: number;
  similarity: number; // 0~1 사이 유사도
}

export interface HashtagToPlaceResponse {
  move: PlaceRecommendation[];  
}

// 2) 카테고리 → 해시태그 추천
export interface CategoryToHashtagRequest {
  category: string;
  viewport: Viewport;
}

export interface CategoryToHashtagResponse {
  tags: Hashtag[];
}

// ─── 일정 생성 & 요약 ──────────────────────────────────

// 식사 선호 정보
export interface MealPreferences {
  breakfast: string[];
  lunch: string[];
  dinner: string[];
}

// 사용자 전체 선호 정보
export interface UserPreferences {
  start_time: string;  
  end_time: string;    
  travel_style: string;
  meal_time_preferences: MealPreferences;
}

// 일정에 추가할 장소 입력 정보
export interface ItineraryPlaceInput {
  name: string;
}

// 일정 생성용 POST Body
export interface ItineraryPostBody {
  date: {
    user_id: string;
    start_date: string;     // "YYYY-MM-DD"
    end_date: string;       // "YYYY-MM-DD"
    arrival_time: string;   // ISO 8601 "HH:mm"
    departure_time: string; // ISO 8601 "HH:mm"
  }
  user: UserPreferences;
  places_by_day: PlacesByDay<ItineraryPlaceInput>;
}

// API 응답에서 받는 장소 요약 정보
export interface PlaceSummary {
  name: string;
  x_cord: number;
  y_cord: number;
  category: string;
}

// 일정 생성 응답
export interface ItineraryResponse {
  places_by_day: PlacesByDay<PlaceSummary>;
}

// 일정 중 장소의 상세 + 시간 정보 포함
export interface ItineraryPlace extends PlaceDetail {
  arrival_str: string;      // ISO 8601 "HH:mm"
  departure_str: string;    // ISO 8601 "HH:mm"
  service_time: number;     // 분 단위
}

export interface InternalItinerary {
  places_by_day: PlacesByDay<ItineraryPlace>;
}

// ─── 경로 계산 ─────────────────────────────────────────

// 경로 요청: 장소 이름 + 서비스 시간
export interface RoutingRequest {
  user_id: string;
  places_by_day: PlacesByDay<{
    name: string;
    service_time: number | null; // 분 단위
  }>;
}

// 경로 계산 결과용 장소 정보
export interface RoutingPlace extends PlaceMarker {
  address: string;
  arrival_str: string;    // ISO 8601 "HH:mm"
  departure_str: string;  // ISO 8601 "HH:mm"
  service_time: number;   // 분 단위
}

// 경로 응답: 계산된 장소별 정보 + 폴리라인
export interface RoutingResponse {
  places_by_day: PlacesByDay<RoutingPlace>;
  path: [number, number][][]; // 다중 경로 좌표 배열
}

// ─── 장소 정보 ────────────────────────────────────────

// 요청: 장소 이름
export interface PlaceDetailRequest {
  name: PlaceName;
}

// 응답: 단일 장소 상세 정보
export interface PlaceDetailResponse {
  places: PlaceDetail;
}

// ─── 장소 검색 ────────────────────────────────────

// 요청: 검색어 전달
export interface PlaceSearchRequest {
  name: PlaceName;
}

// 응답: 검색 결과 리스트
export interface PlaceSearchResponse {
  search: { name: PlaceName }[];
}