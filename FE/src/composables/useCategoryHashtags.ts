import { ref } from 'vue'
import { useCategoryToHashtagApi } from '@/composables/api/useCategoryToHashtagApi'
import type { Hashtag, Viewport, Category } from '@/types/common'

export function useCategoryHashtags() {
  const showHashtag = ref(false)
  const selectedCategory = ref<Category | null>(null)
  const hashtags = ref<Hashtag[]>([])

  const { fetchTags } = useCategoryToHashtagApi()

  // 카테고리 클릭 시 해시태그 로드
  const toggleCategory = async (category: Category, viewport: Viewport) => {
    if (selectedCategory.value === category && showHashtag.value) {
      showHashtag.value = false
      return
    }

    selectedCategory.value = category

    console.log('[useCategoryHashtags] 카테고리 선택:', category)
    console.log('[useCategoryHashtags] 뷰포트:', viewport)

    // 카테고리와 viewport를 통해 해시태그 목록을 받아옴
    const { success, data, error } = await fetchTags({ category, viewport })

    if (success) {
      hashtags.value = data  // 해시태그 배열을 저장
      showHashtag.value = true  // 해시태그 표시
    } else {
      hashtags.value = []  // 빈 배열로 설정
      showHashtag.value = false  // 해시태그 숨기기
      console.warn(`[useCategoryHashtags] 해시태그 로딩 실패: ${error}`)
    }
  }

  return {
    showHashtag,
    selectedCategory,
    hashtags,
    toggleCategory
  }
}
