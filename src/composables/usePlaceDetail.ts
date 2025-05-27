// usePlaceDetail.ts
import { usePlaceDetailApi } from '@/composables/api/usePlaceDetailApi';
import { ref } from 'vue';
import type { PlaceSearchRequest, PlaceDetail } from '@/types/api';

export function usePlaceDetail() {
  const { fetchPlace, isLoading, error } = usePlaceDetailApi(); 
  const placeDetail = ref<PlaceDetail | null>(null);  

  const fetchPlaceDetail = async (placeData: PlaceSearchRequest) => {
    const requestBody = { name: placeData.name };

    try {
      const result = await fetchPlace(requestBody);
      
      placeDetail.value = result.success ? result.data : null;
    } catch (err) {
      console.error('API 호출 실패:', err);
    }
  };

  return { placeDetail, fetchPlaceDetail, isLoading, error };
}
