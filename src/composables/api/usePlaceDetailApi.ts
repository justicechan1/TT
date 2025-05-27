// usePlaceDetailApi.ts

import { useTrendyTripApi } from '@/composables/useTrendyTripApi';
import type {
  PlaceDetailRequest,
  PlaceDetailResponse,
  PlaceDetail
} from '@/types/api';
import { ref } from 'vue';

type FetchPlaceResult =
  | { success: true; data: PlaceDetail; error: null }
  | { success: false; data: null; error: Error };

export function usePlaceDetailApi() {
  const { postData } = useTrendyTripApi();
  const isLoading = ref(false);
  const error = ref<Error | null>(null);

  async function fetchPlace(
    body: PlaceDetailRequest
  ): Promise<FetchPlaceResult> {
    isLoading.value = true;
    error.value = null;

    try {
      const resp = await postData<PlaceDetailResponse>(
        '/api/places/select_place',
        body
      );

      if (!resp.success || !resp.data) {
        console.warn('[PlaceDetailAPI] 응답 비정상:', resp);
        throw new Error('장소 상세 정보 응답이 비어 있습니다');
      }

      const detail = resp.data.places; // 단일 장소지만 key가 'places'
      return { success: true, data: detail, error: null };
    } catch (e: any) {
      const err = e instanceof Error ? e : new Error(String(e));
      error.value = err;
      return { success: false, data: null, error: err };
    } finally {
      isLoading.value = false;
    }
  }

  return { fetchPlace, isLoading, error };
}
