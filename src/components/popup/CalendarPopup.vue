<template>
  <div class="popup-container">
    <header>
      <h2>{{ trip_area }}여행</h2>
      <p>{{ startDay }} ~ {{ endDay }}</p>
      <p>총 {{ tripday }}일</p>
      <select v-model="selectedDay" @change="SelectedDay" class="select-day">
        <option v-for="n in tripday" :key="n" :value="n">Day {{ n }}</option>
      </select>
    </header>

    <article class="choose">
      <ItineraryTimeline v-if="currentVisits.length > 0" :visits="currentVisits"
        @get-place-info="handlePlaceInfo" />
      <p v-else>선택된 일차에 방문지가 없습니다.</p>
    </article>

    <footer>
      <button class="button-close" @click="emit('close')">닫기❌</button>
    </footer>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/store/userStore'
import { useItineraryStore } from '@/store/itineraryStore'
import ItineraryTimeline from '@/components/common/ItineraryTimeline.vue'
import type { PlaceSearchRequest } from '@/types/api';
import { usePlaceDetailApi } from '@/composables/api/usePlaceDetailApi';

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'select-day', coords: { x: number; y: number }[]): void
  (e: 'get-place-info', place: any): void
}>()

const selectedDay = ref<number>(1)

const userStore = useUserStore()
const itineraryStore = useItineraryStore()

const trip_area = userStore.area
const startDay = userStore.startDate
const endDay = userStore.endDate
const tripday = userStore.tripDays

const currentVisits = computed(() => {
  const { places } = itineraryStore.getProcessedPlaces(selectedDay.value)
  console.log(`현재 선택된 일차의 방문지: Day ${selectedDay.value}`, places)
  return places
})

const SelectedDay = () => {
  console.log(`선택된 옵션: Day ${selectedDay.value}`)
  const coordinates = currentVisits.value.map((visit) => ({
    x: visit.x_cord,
    y: visit.y_cord
  }))
  emit('select-day', coordinates)
}

onMounted(() => {
  SelectedDay()
})

// usePlaceDetailApi 훅을 사용하여 API 호출 함수 정의
const { fetchPlace, isLoading, error } = usePlaceDetailApi()

// 장소 상세 정보를 처리하는 함수
const handlePlaceInfo = async (placeData: PlaceSearchRequest) => {
  console.log('클릭된 장소 이름:', placeData.name);  
  console.log(placeData);

  const requestBody = {
    name: placeData.name,  // 여기에 추가 필드가 필요하면 요청 본문에 추가
  }

  console.log('장소 상세 정보 요청 본문:', requestBody);

  try {
    // 로딩 상태 처리
    isLoading.value = true;
    error.value = null;  // 에러 초기화

    // API 호출하여 장소 상세 정보 가져오기
    const result = await fetchPlace(requestBody);

    if (result.success) {
      console.log('장소 상세 정보:', result.data);
      // 성공적으로 받은 장소 상세 정보를 UI에 반영
      emit('get-place-info', result.data);  // 필요시 부모 컴포넌트로 데이터 전달
    } else {
      console.error('장소 상세 정보 오류:', result.error);
      error.value = result.error;  // 오류 발생 시 에러 상태 처리
    }
  } catch (err) {
    console.error('API 호출 실패:', err);
    error.value = err instanceof Error ? err : new Error('API 호출 중 오류 발생');
  } finally {
    // 로딩 완료 처리
    isLoading.value = false;
  }
}
</script>

<style scoped>
@import "@/styles/popup.css";

/* 선택된 날짜 드롭다운 스타일 */
.select-day {
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
  background-color: #f9f9f9;
  cursor: pointer;
}

.select-day:hover {
  border-color: #888;
}

/* 중간 영역 */
article.choose {
  display: flex;
  flex-direction: column;
  gap: 12px;
  flex-grow: 1;
  overflow-y: auto;
}

article.choose p {
  font-size: 1rem;
  color: #888;
  text-align: center;
}

/* 버튼 스타일 */
button {
  padding: 10px 16px;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  width: 100%; /* 버튼 크기를 100%로 통일 */
}

/* 경고 메시지 스타일 */
article.choose p {
  font-size: 1rem;
  color: #999;
  text-align: center;
  font-style: italic;
  padding: 8px;
  background-color: #f8f8f8;
  border-radius: 4px;
}
</style>
