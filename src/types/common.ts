// 공통으로 쓰이는 기본 타입들

// 장소 이름
export type PlaceName = string;

// 해시태그
export interface Hashtag {
  hashtag_name: string;
}

// 지도 화면 범위
export interface Viewport {
  min_x: number;
  min_y: number;
  max_x: number;
  max_y: number;
}

// 날짜(또는 인덱스)별 장소 리스트 묶기용 제네릭
export type PlacesByDay<T> = Record<number, T[]>;

// 카테고리 
export type Category = string;