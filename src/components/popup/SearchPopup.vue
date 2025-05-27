<template>
  <div class="popup-container">
    <header>
      <p>어떤 관광명소를 찾고 계시나요?</p>
      <h3>🔎장소를 검색해주세요</h3>
      <div class="search-container">
        <input 
          v-model="searchQuery" 
          type="text" 
          placeholder="장소를 입력하세요" 
          class="input-search" 
          aria-label="장소 검색"
          @input="onSearchInput"
          @keyup.enter="searchPlaces"
        />
        <button @click="searchPlaces" class="search-button">검색</button> 
      </div>
    </header>

    <article class="place-list">
      <p>✅ 추천 장소</p>
      <ul>
        <li 
          v-for="(place, index) in filteredPlaces" 
          :key="index" 
          @click="selectPlace(place)"
        >
          <span v-html="highlightMatchedText(place.name)"></span> 
        </li>
      </ul>
    </article>

    <footer>
      <button class="button-close" @click="emit('close')">닫기❌</button>
    </footer>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed } from 'vue';
import { usePlaceSearchApi } from '@/composables/api/usePlaceSearchApi';
import type { PlaceSearchRequest } from '@/types/api';

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'select-place', place: any): void;
}>();

const searchQuery = ref('');
const places = ref<any[]>([]);

// 가상 데이터 (constants)
const constants = {
  exampleSearchResult: [
    { name: '경복궁' },
    { name: 'N 서울타워' },
    { name: '명동' },
    { name: '한강공원' },
    { name: '이태원' },
  ],
};

const { fetchSearch } = usePlaceSearchApi(); 

let debounceTimeout: ReturnType<typeof setTimeout> | null = null;

const onSearchInput = () => {
  if (debounceTimeout) {
    clearTimeout(debounceTimeout);
  }

  debounceTimeout = setTimeout(async () => {
    if (!searchQuery.value) {
      places.value = []; // 검색어가 없으면 결과 비우기
      return;
    }

    const requestBody: PlaceSearchRequest = {
      name: searchQuery.value, 
    };``

    // 요청 내용 콘솔에 찍기
    console.log('검색 요청:', requestBody);

    // 가상 데이터에서 필터링하여 결과 표시
    const filteredResults = constants.exampleSearchResult.filter(place =>
      place.name.toLowerCase().includes(searchQuery.value.toLowerCase())
    );

    console.log('필터링된 결과:', filteredResults);

    places.value = filteredResults; // 필터링된 결과로 places 배열 업데이트

    // 실제 검색 API 호출을 주석 처리
    // const result = await fetchSearch(requestBody);
    // if (result.success) {
    //   places.value = result.data || []; 
    // } else {
    //   console.error('검색 오류:', result.error);
    // }
  }, 300);
};

const filteredPlaces = computed(() => {
  if (!searchQuery.value) {
    return places.value;
  }
  return places.value.filter(place =>
    place.toLowerCase().includes(searchQuery.value.toLowerCase())
  );
});

const selectPlace = (place: any) => {
  emit('select-place', place); // 선택된 장소 정보 emit
};

// 검색어 강조 처리
const highlightMatchedText = (text: string) => {
  if (!searchQuery.value) return text;
  const regex = new RegExp(`(${searchQuery.value})`, 'gi');
  return text.replace(regex, '<mark>$1</mark>'); // <mark> 태그로 강조
};

// 검색 버튼이나 엔터키로 검색을 실행하는 함수
const searchPlaces = () => {
  if (!searchQuery.value) {
    return; // 검색어가 비어 있으면 아무 것도 하지 않음
  }
  console.log('검색:', searchQuery.value);
};
</script>

<style scoped>
@import "@/styles/popup.css";

/* 검색창과 버튼 */
.search-container {
  display: flex;
  align-items: center;
  gap: 8px; 
}

.input-search {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
}

.search-button {
  padding: 8px 16px;
  background-color: skyblue;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.search-button:hover {
  background-color: deepskyblue;
}

/* 장소 목록 */
.place-list ul {
  list-style-type: none;
  padding: 0;
  overflow-y: auto; /* 장소 목록이 넘칠 때 스크롤 처리 */
  max-height: 200px; /* 장소 목록의 최대 높이 */
}

.place-list li {
  padding: 8px;
  cursor: pointer;
  border-bottom: 1px solid #ccc;
}

.place-list li:hover {
  background-color: #f0f0f0;
}

</style>
