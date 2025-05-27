<template>
  <div class="popup-container">
    <header>
      <h2>📜 다운로드</h2>
    </header>

    <article class="save-list">
      <!-- 저장 목록 또는 다운로드 옵션 등 향후 추가 예정 -->
    </article>

    <footer>
      <button class="button-close" @click="emit('close')">닫기❌</button>
    </footer>
  </div>
</template>

<script lang="ts" setup>
const emit = defineEmits<{
  (e: 'close'): void
}>()
</script>

<style scoped>
@import "@/styles/popup.css";
</style>
