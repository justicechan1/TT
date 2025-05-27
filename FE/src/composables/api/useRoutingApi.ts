// src/composables/api/useRoutingApi.ts

import { ref } from 'vue'
import { useTrendyTripApi } from '@/composables/useTrendyTripApi'
import type {
  RoutingRequest,
  RoutingResponse
} from '@/types/api'

type FetchRoutingResult =
  | { success: true; data: RoutingResponse; error: null }
  | { success: false; data: null; error: Error }

export function useRoutingApi() {
  const { postData } = useTrendyTripApi()
  const isLoading = ref(false)
  const error = ref<Error | null>(null)

  async function fetchRoute(
    body: RoutingRequest
  ): Promise<FetchRoutingResult> {
    isLoading.value = true
    error.value = null

    try {
      const resp = await postData<RoutingResponse>(
        '/api/users/schedules/schedul',
        body
      )

      if (!resp.success || !resp.data) {
        console.warn('[useRoutingApi] 응답 비정상:', resp)
        throw new Error('경로 계산 응답이 비어 있습니다')
      }

      return { success: true, data: resp.data, error: null }
    } catch (e: any) {
      const err = e instanceof Error ? e : new Error(String(e))
      error.value = err
      return { success: false, data: null, error: err }
    } finally {
      isLoading.value = false
    }
  }

  return { fetchRoute, isLoading, error }
}
