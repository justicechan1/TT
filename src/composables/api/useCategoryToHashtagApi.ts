// src/composables/api/useCategoryToHashtagApi.ts

import type {
  CategoryToHashtagRequest,
  CategoryToHashtagResponse,
} from '@/types/api';
import { useTrendyTripApi } from '@/composables/useTrendyTripApi';
import { ref } from 'vue';
import type { Hashtag } from '@/types/common';

type FetchTagsResult =
  | { success: true; data: Hashtag[]; error: null }
  | { success: false; data: null; error: Error };

export function useCategoryToHashtagApi() {
  const { postData } = useTrendyTripApi();
  const isLoading = ref(false);
  const error = ref<Error | null>(null);

  async function fetchTags(
    body: CategoryToHashtagRequest
  ): Promise<FetchTagsResult> {
    isLoading.value = true;
    error.value = null;
    console.debug('[useCategoryToHashtagApi] request body:', body);

    try {
      const resp = await postData<CategoryToHashtagResponse>(
        '/api/users/maps/hashtage',
        body
      );
      console.debug('[useCategoryToHashtagApi] raw response:', resp);

      if (!resp.success || !resp.data) {
        throw new Error('태그 추천 응답이 비어 있습니다');
      }

      // 타입 정의에 따르면 resp.data.tags: Hashtag[]
      const tags = resp.data.tags;
      console.debug('[useCategoryToHashtagApi] parsed tags:', tags);

      return { success: true, data: tags, error: null };
    } catch (e: any) {
      const err = e instanceof Error ? e : new Error(String(e));
      error.value = err;
      console.error('[useCategoryToHashtagApi] error:', err);
      return { success: false, data: null, error: err };
    } finally {
      isLoading.value = false;
    }
  }

  return { fetchTags, isLoading, error };
}
