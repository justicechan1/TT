<template>
  <div id="map" class="map-view"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick, defineEmits } from 'vue'
import { useNaverMap } from '@/services/useNaverMap'

interface PlaceMarker {
  name: string
  category: string
  x_cord: number
  y_cord: number
}

const props = defineProps<{
  places: PlaceMarker[]
}>()

const centerLat = props.places[0]?.y_cord ?? 33.4
const centerLng = props.places[0]?.x_cord ?? 126.55

// useNaverMap 훅에서 지도 초기화만 처리
const { map } = useNaverMap(centerLat, centerLng)

const isMapReady = ref(false)
const marker = ref<naver.maps.Marker | null>(null)

// 부모에게 map 객체를 전달하기 위한 emit
const emit = defineEmits<{
  (event: 'mapReady', map: naver.maps.Map): void
}>()

// 1. watch로 map.value의 초기화 상태 감지
watch(map, (newMap) => {
  if (newMap) {
    // map 객체가 초기화된 후 작업 처리
    console.log('지도 객체가 준비되었습니다:', newMap)
    console.log(newMap.getBounds())  // 지도 경계 확인

    // 지도 중앙에 마커 추가
    const latLng = new window.naver.maps.LatLng(centerLat, centerLng)
    marker.value = new window.naver.maps.Marker({
      position: latLng,
      map: newMap,
    })

    // 마커 클릭 시 지도 이동
    window.naver.maps.Event.addListener(marker.value, 'click', () => {
      if (newMap) {
        newMap.setCenter(latLng)  // 클릭 시 지도 중앙을 마커 위치로 이동
        newMap.setZoom(15)  // 클릭 시 줌 레벨을 15로 설정
      }
    })

    // 부모에게 map 객체 전달
    emit('mapReady', newMap)
  }
})

// 2. 컴포넌트가 마운트되면 nextTick으로 map 초기화 상태 확인
onMounted(() => {
  nextTick(() => {
    if (map.value) {
      isMapReady.value = true
      console.log('컴포넌트가 마운트되었습니다. 지도 객체:', map.value)
      console.log(map.value?.getBounds())  // 지도 경계 확인

      // 지도 중앙에 마커 추가
      const latLng = new window.naver.maps.LatLng(centerLat, centerLng)
      marker.value = new window.naver.maps.Marker({
        position: latLng,
        map: map.value,
      })

      // 마커 클릭 시 지도 이동
      window.naver.maps.Event.addListener(marker.value, 'click', () => {
        if (map.value) {
          map.value.setCenter(latLng)  
          map.value.setZoom(15)  
        }
      })

      // 부모에게 map 객체 전달
      emit('mapReady', map.value)
    }
  })
})
</script>

<style scoped>
.map-view {
  width: 100%;
  height: 100%;
}
</style>
