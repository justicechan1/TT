<template>
  <nav class="side">
    <button @click="togglePopup('search')">🔍</button>
    <button @click="togglePopup('calendar')">📆</button>
    <button @click="togglePopup('save')">💾</button>
    <button @click="togglePopup('place')">❓</button>

    <!-- 팝업도 같이 포함 -->
    <transition name="slide-popup">
      <component v-if="activeComponent" :is="activeComponent" v-bind="activeProps" class="popup-panel"
        @close="closePopups" />
    </transition>
  </nav>
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
  togglePopup,
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
.side {
  position: absolute;
  top: 5%;
  left: 1vw;
  width: 5vw;
  height: 80%;
  border: 2px solid skyblue;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: center;

  background: white;
  border-radius: 12px;
  padding: 12px 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);

  z-index: 10;
  transition: box-shadow 0.3s ease, transform 0.3s ease;
}

.side button {
  width: 40px;
  height: 40px;
  font-size: 24px;
  margin: 10px 0;
  background: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.side button:hover {
  background: #e0f6ff;
}

.popup-panel {
  position: absolute;
  left: calc(100% + 10px);
  top: 0;
}

.slide-popup-enter-active,
.slide-popup-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.slide-popup-enter-from,
.slide-popup-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.slide-popup-enter-to,
.slide-popup-leave-from {
  opacity: 1;
  transform: translateY(0);
}
</style>
