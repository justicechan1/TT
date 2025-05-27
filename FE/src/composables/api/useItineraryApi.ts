// src/composables/api/useItineraryApi.ts

import type {
  ItineraryPostBody,
  ItineraryResponse,
  InternalItinerary,
  ItineraryPlace,
} from '@/types/api';
import { useTrendyTripApi } from '@/composables/useTrendyTripApi';
import { ref } from 'vue';
import { convertPlaceSummaryToItineraryPlace } from '@/utils/converters';

type CreateItineraryResult =
  | { success: true; data: InternalItinerary; error: null }
  | { success: false; data: null; error: Error };

export function useItineraryApi() {
  const { postData } = useTrendyTripApi();
  const isLoading = ref(false);
  const error = ref<Error | null>(null);

  async function createItinerary(
    body: ItineraryPostBody
  ): Promise<CreateItineraryResult> {
    isLoading.value = true;
    error.value = null;
    console.debug('[useItineraryApi] request body:', body);

    try {
      const resp = await postData<ItineraryResponse>(
        '/api/users/schedules/init',
        body
      );
      console.debug('[useItineraryApi] raw response:', resp);

      if (!resp.success || !resp.data) {
        const e = new Error('API 응답이 비어있습니다');
        console.error('[useItineraryApi]', e);
        throw e;
      }

      // API 요약 응답을 내부 모델로 변환
      const converted: Record<number, ItineraryPlace[]> = {};
      for (const [dayKey, list] of Object.entries(resp.data.places_by_day)) {
        const day = Number(dayKey);
        const arr: ItineraryPlace[] = [];

        for (const summary of list) {
          try {
            arr.push(convertPlaceSummaryToItineraryPlace(summary));
          } catch (convErr) {
            console.warn(
              `[useItineraryApi] 변환 실패 (day=${day}):`,
              summary,
              convErr
            );
          }
        }

        converted[day] = arr;
      }

      const internal: InternalItinerary = { places_by_day: converted };
      console.debug('[useItineraryApi] converted internal:', internal);

      return { success: true, data: internal, error: null };
    } catch (e: any) {
      const err = e instanceof Error ? e : new Error(String(e));
      error.value = err;
      console.error('[useItineraryApi] caught error:', err);
      return { success: false, data: null, error: err };
    } finally {
      isLoading.value = false;
    }
  }

  return { createItinerary, isLoading, error };
}
