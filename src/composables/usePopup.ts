import { ref } from 'vue'

const isCalendarPopupVisible  = ref(false)
const isSearchPopupVisible    = ref(false)
const isSavePopupVisible      = ref(false)
const isPlacePopupVisible     = ref(false)
const isAddPlaceVisible       = ref(false)
const isRemovePlaceVisible    = ref(false)
const showHashtag             = ref(false)

const selectedPlace           = ref<{ name: string; address: string; image_urls: string[] } | null>(null)
const currentPopupStyle       = ref<Record<string, string>>({ right: '20px', top: '10%' })

export function usePopup() {
  const closePopups = () => {
    isCalendarPopupVisible.value = false
    isSearchPopupVisible.value   = false
    isSavePopupVisible.value     = false
    isPlacePopupVisible.value    = false
    isAddPlaceVisible.value      = false
    isRemovePlaceVisible.value   = false
    showHashtag.value            = false
  }

  const togglePopup = (
    type: 'calendar' | 'search' | 'save' | 'place' | 'addPlace' | 'removePlace' | 'hashtag'
  ) => {
    if (type === 'hashtag') {
      showHashtag.value = !showHashtag.value
      return
    }

    const mapping = {
      calendar: isCalendarPopupVisible,
      search: isSearchPopupVisible,
      save: isSavePopupVisible,
      place: isPlacePopupVisible,
      addPlace: isAddPlaceVisible,
      removePlace: isRemovePlaceVisible
    }

    const targetRef = mapping[type]

    const wasOpen = targetRef.value
    closePopups()

    if (!wasOpen) {
      targetRef.value = true
    }
  }

  return {
    // state
    isCalendarPopupVisible,
    isSearchPopupVisible,
    isSavePopupVisible,
    isPlacePopupVisible,
    isAddPlaceVisible,
    isRemovePlaceVisible,
    showHashtag,
    selectedPlace,
    currentPopupStyle,
    // actions
    togglePopup,
    closePopups
  }
}
