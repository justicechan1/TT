<template>
  <transition name="slide-popup">
    <component v-if="activeComponent" :is="activeComponent" v-bind="activeProps" class="popup-panel"
      @close="closePopups" />
  </transition>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { usePopup } from '@/composables/usePopup'

import CalPop from '@/components/popup/CalendarPopup.vue'
import SearchPop from '@/components/popup/SearchPopup.vue'
import SavePop from '@/components/popup/SavePopup.vue'
import PlacePop from '@/components/popup/PlacePopup.vue'

const {
  isCalendarPopupVisible,
  isSearchPopupVisible,
  isSavePopupVisible,
  isPlacePopupVisible,
  selectedPlace,
  currentPopupStyle,
  closePopups
} = usePopup()

const activeComponent = computed(() => {
  if (isCalendarPopupVisible.value) return CalPop
  if (isSearchPopupVisible.value) return SearchPop
  if (isSavePopupVisible.value) return SavePop
  if (isPlacePopupVisible.value && selectedPlace.value) return PlacePop
  return null
})

const activeProps = computed(() => {
  if (activeComponent.value === PlacePop) {
    return { place: selectedPlace.value, style: currentPopupStyle.value }
  }
  return {}
})
</script>

<style scoped>
.popup-panel {
  position: fixed;
  top: 50%;
  left: 30%;
  transform: translate(-50%, -50%);
  z-index: 1000;

  width: 30vw;
  max-width: 480px;
  max-height: 90vh;

  background-color: transparent;
  /* 내부 .pop이 배경 담당 */
  padding: 0;
  overflow: hidden;
  /* 외부 스크롤 방지 */
  display: flex;
  flex-direction: column;
}

/* 트랜지션 예시 */
.slide-popup-enter-active,
.slide-popup-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.slide-popup-enter-from,
.slide-popup-leave-to {
  opacity: 0;
  transform: translate(-50%, -60%) scale(0.95);
}

.slide-popup-enter-to,
.slide-popup-leave-from {
  opacity: 1;
  transform: translate(-50%, -50%) scale(1);
}
</style>
