export const areas = [
  '서울', '경기/인천', '충청', '강원',
  '경상', '전라', '제주', '부산',
  '대구', '광주', '대전', '세종'
]

export const CATEGORY_HASHTAGS: Record<string, { hashtag_name: string }[]> = {
  tourist: [
    { hashtag_name: '관광명소' },
    { hashtag_name: '문화유산' },
    { hashtag_name: '자연경관' }
  ],
  cafe: [
    { hashtag_name: '감성카페' },
    { hashtag_name: '디저트맛집' },
    { hashtag_name: '브런치' }
  ],
  restaurant: [
    { hashtag_name: '한식' },
    { hashtag_name: '일식' },
    { hashtag_name: '양식' }
  ],
  accommodation: [
    { hashtag_name: '호텔' },
    { hashtag_name: '게스트하우스' },
    { hashtag_name: '에어비앤비' }
  ]
}

export const BACKEND_URL = 'http://localhost:8000'
