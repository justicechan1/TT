<template>
  <div class="map-page">
    <div class="map-wrapper">
      <!-- MapContainer에 마커 데이터 전달 -->
      <MapContainer
        class="map-bg"
        :places="markerPlaces"
        @mapReady="handleMap"
      />

      <!-- 사이드바: 팝업 포함 -->
      <Sidebar />

      <!-- 카테고리 버튼 -->
      <div id="category_btn">
        <button class="category-button" @click="handleCategoryClick('tourist')">관광명소</button>
        <button class="category-button" @click="handleCategoryClick('cafe')">카페</button>
        <button class="category-button" @click="handleCategoryClick('restaurant')">음식점</button>
        <button class="category-button" @click="handleCategoryClick('accommodation')">숙소</button>
      </div>

      <!-- 해시태그 버튼 -->
      <div id="hashtag_btn" v-if="showHashtag">
        <HashtagButtons
          :selectedHashtag="selectedHashtag"
          :hashtags="hashtags"
          @select-hashtag="handleSelectHashtag"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useItineraryStore } from '@/store/itineraryStore'

import MapContainer from '@/components/map/MapContainer.vue'
import Sidebar from '@/components/map/Sidebar.vue'
import HashtagButtons from '@/components/ui/buttons/HashtagButtons.vue'

import { useCategoryHashtags } from '@/composables/useCategoryHashtags'
import { useSelectedHashtag } from '@/composables/useSelectedHashtag'
import { getMapBounds } from '@/utils/map'

import type { Hashtag, Category } from '@/types/common'

import '@/styles/map.css'

const itineraryStore = useItineraryStore()
const router = useRouter()

// 마커 데이터
const markerPlaces = computed(() => {
  const current = itineraryStore.current
  if (!current) return []

  const firstPlace = current.places_by_day[1]?.[0]
  if (!firstPlace) {
    console.warn('⚠️ 첫째 날에 장소가 없습니다.')
    return []
  }

  return [{
    name: firstPlace.name,
    category: firstPlace.category,
    x_cord: firstPlace.x_cord,
    y_cord: firstPlace.y_cord,
  }]
})

// 지도 객체를 저장할 ref
const mapRef = ref<naver.maps.Map | null>(null)

// 부모에서 map 객체를 받는 함수
const handleMap = (map: naver.maps.Map) => {
  console.log('지도 객체가 부모로 전달되었습니다:', map)
  mapRef.value = map  
}

// 카테고리 해시태그 관련 훅 사용
const {
  showHashtag,
  selectedCategory,
  hashtags,
  toggleCategory
} = useCategoryHashtags()

// 해시태그 관련 훅 사용
const {
  selectedHashtag,
  selectHashtag
} = useSelectedHashtag()

// 카테고리 클릭 처리
const handleCategoryClick = async (category: Category) => {
  if (mapRef.value) {
    console.log(`🔍 카테고리 클릭: ${category}`)
    const viewport = getMapBounds(mapRef.value)   // 지도 범위 가져오기
    console.log(`🔍 카테고리 클릭: ${category}, 지도 범위:`, viewport)  // 로그 추가
    await toggleCategory(category, viewport)  // getBounds로 viewport를 넘기기
  }
}

// 해시태그 클릭 처리
const handleSelectHashtag = async (hashtag: Hashtag) => {
  if (mapRef.value) {
    const viewport = getMapBounds(mapRef.value)  // 지도 범위 가져오기
    console.log(`🔍 해시태그 클릭: ${hashtag.hashtag_name}, 지도 범위:`, viewport)  // 로그 추가

    // selectedCategory.value가 null인 경우를 처리
    if (selectedCategory.value) {
      // selectedCategory.value가 string일 경우 Category로 변환하여 selectHashtag 호출
      await selectHashtag(selectedCategory.value as Category, hashtag, viewport)
    } else {
      console.warn('❌ 카테고리가 선택되지 않았습니다.')
    }
  }
}
</script>

<style scoped>
</style>
