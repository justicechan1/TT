// src/composables/api/useHashtagToPlaceApi.ts

import { useTrendyTripApi } from '@/composables/useTrendyTripApi';
import type {
  HashtagToPlaceRequest,
  HashtagToPlaceResponse,
  PlaceRecommendation
} from '@/types/api';
import { ref } from 'vue';

type FetchPlacesResult =
  | { success: true; data: PlaceRecommendation[]; error: null }
  | { success: false; data: null; error: Error };

export function useHashtagToPlaceApi() {
  const { postData } = useTrendyTripApi();
  const isLoading = ref(false);
  const error = ref<Error | null>(null);

  async function fetchPlaces(
    body: HashtagToPlaceRequest
  ): Promise<FetchPlacesResult> {
    isLoading.value = true;
    error.value = null;

    try {
      const resp = await postData<HashtagToPlaceResponse>(
        '/api/users/maps/select_hashtage',
        body
      );

      if (!resp.success || !resp.data) {
        throw new Error('장소 추천 응답이 비어 있습니다');
      }

      const places = resp.data.move;
      return { success: true, data: places, error: null };
    } catch (e: any) {
      const err = e instanceof Error ? e : new Error(String(e));
      error.value = err;
      return { success: false, data: null, error: err };
    } finally {
      isLoading.value = false;
    }
  }

  return { fetchPlaces, isLoading, error };
}
