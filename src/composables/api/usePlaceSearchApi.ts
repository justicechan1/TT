// src/composables/api/usePlaceSearchApi.ts

import { useTrendyTripApi } from '@/composables/useTrendyTripApi';
import type {
  PlaceSearchRequest,
  PlaceSearchResponse
} from '@/types/api';
import { ref } from 'vue';

type FetchSearchResult =
  | { success: true; data: string[]; error: null }
  | { success: false; data: null; error: Error };

export function usePlaceSearchApi() {
  const { postData } = useTrendyTripApi();
  const isLoading = ref(false);
  const error = ref<Error | null>(null);

  async function fetchSearch(
    body: PlaceSearchRequest
  ): Promise<FetchSearchResult> {
    isLoading.value = true;
    error.value = null;

    try {
      const resp = await postData<PlaceSearchResponse>(
        '/api/places/search',
        body
      );

      if (!resp.success || !resp.data) {
        console.warn('[usePlaceSearchApi] 응답 비정상:', resp);
        throw new Error('장소 검색 응답이 비어 있습니다');
      }

      // search 배열에서 name만 추출
      const names = resp.data.search.map(item => item.name);
      return { success: true, data: names, error: null };
    } catch (e: any) {
      const err = e instanceof Error ? e : new Error(String(e));
      error.value = err;
      return { success: false, data: null, error: err };
    } finally {
      isLoading.value = false;
    }
  }

  return { fetchSearch, isLoading, error };
}
