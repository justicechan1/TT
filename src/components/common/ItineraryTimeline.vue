<template>
  <v-timeline align="start" side="end">
    <v-timeline-item v-for="(visit, index) in visits" :key="index" dot-color="blue" size="small">
      <div class="d-flex">
        <strong class="me-4">{{ index + 1 }}</strong>  <!-- order로 인덱스 사용 -->
        <div @click="getplaceInfo(visit)" style="cursor: pointer;">
          <!-- 장소 이름과 카테고리 -->
          <strong class="place-name">{{ visit.name }}</strong>
          <span class="category-label">{{ visit.category }}</span>
          
          <div class="text-caption">
            <!-- 이동시간과 체류시간 -->
            <div>이동시간: {{ visit.arrival_str }} ~ {{ visit.departure_str }}</div>
            <div>체류시간: {{ visit.stay_duration }} 분</div>
          </div>
        </div>
      </div>
    </v-timeline-item>
  </v-timeline>
</template>

<script lang="ts">
import type { PlaceSearchRequest } from '@/types/api';

export default {
  name: 'ItineraryTimeline',
  props: {
    visits: {
      type: Array as () => Array<PlaceSearchRequest>,  
      required: true
    }
  },
  methods: {
    getplaceInfo(visit: PlaceSearchRequest) {  
      console.log('클릭된 방문지 정보:', visit);

      // 새로운 객체를 만들어서 name 속성만 설정
      const placeSearchRequest: PlaceSearchRequest = {
        name: visit.name
      };
      
      // 생성한 객체를 emit으로 부모에게 전달
      this.$emit('get-place-info', placeSearchRequest);  
    }
  }
}
</script>

<style scoped>
.place-name {
  font-size: 16px;
  font-weight: bold;
  color: #3a3a3a;
}

.category-label {
  display: block;
  font-size: 14px;
  color: #999;
  margin-top: 4px;
}

.text-caption {
  font-size: 12px;
  color: #666;
}

.v-timeline-item {
  background-color: #f9f9f9;
  border-radius: 8px;
  margin: 5px 0;
  padding: 10px;
}

.v-timeline-item .d-flex {
  align-items: center;
}
</style>
