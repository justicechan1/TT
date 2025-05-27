<template>
  <div class="pop" v-if="place">
    <header>
      <h2>{{ place.name }}</h2>
      <p>{{ place.address }}</p>
    </header>

    <article>
      <div class="image-slider" v-if="place.image_urls && place.image_urls.length">
        <div class="image-container">
          <img v-for="(image, index) in place.image_urls" :key="index" :src="image" :alt="`Image ${index + 1}`"
            class="slider-image" />
        </div>
      </div>
    </article>

    <footer>
      <button class="button-add" @click="emit('open-add-place')">추가➕</button>
      <button class="button-close" @click="emit('close')">닫기❌</button>
    </footer>
  </div>
  <div v-else>
    <p>장소 정보가 없습니다.</p>
  </div>
</template>

<script lang="ts" setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps<{
  place: { name: string; address: string; image_urls: string[] } | null
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'open-add-place'): void
}>()
</script>

<style scoped>
@import "@/styles/popup.css";
</style>
