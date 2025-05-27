import { ref } from 'vue'
import { useHashtagToPlaceApi } from '@/composables/api/useHashtagToPlaceApi'
import type { HashtagToPlaceRequest } from '@/types/api'
import type { Hashtag, Viewport, Category } from '@/types/common'

export function useSelectedHashtag() {
  // selectedHashtag는 단일 Hashtag를 저장하는 Ref입니다.
  const selectedHashtag = ref<Hashtag | null>(null)

  console.log('[useSelectedHashtag] ')

  const { fetchPlaces } = useHashtagToPlaceApi()  // 장소를 가져오는 API 훅

  // 선택된 해시태그와 관련된 장소를 불러오는 함수
  const selectHashtag = async (category: Category, hashtag: Hashtag, viewport: Viewport) => {
    // 선택된 해시태그를 업데이트
    selectedHashtag.value = hashtag

    console.log('✅ 선택된 해시태그:', hashtag)

    if (hashtag) {
      // 해시태그 객체에서 hashtag_name을 가져와서 사용
      const requestBody: HashtagToPlaceRequest = {
        category: category, // 카테고리 이름
        tag: [hashtag],  // `hashtag`를 배열로 감싸서 전달
        viewport // viewport를 추가
      }

      const { success, data, error } = await fetchPlaces(requestBody)

      if (success) {
        // 장소 데이터를 다루는 로직 추가 가능
        console.log('💡 불러온 장소:', data)
        // 여기서 결과를 화면에 표시하는 상태로 관리하면 된다
      } else {
        console.warn('❌ 장소 로딩 실패:', error)
      }
    }
  }

  return {
    selectedHashtag,
    selectHashtag
  }
}
