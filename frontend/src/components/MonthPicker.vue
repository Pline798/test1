<script setup>
defineProps({ year: Number, month: Number })
const emit = defineEmits(['prev', 'next'])
</script>

<template>
  <div class="month-nav">
    <button class="btn-nav" @click="emit('prev')">‹</button>
    <span class="month-label">{{ year }}年{{ month }}月</span>
    <button class="btn-nav" @click="emit('next')">›</button>
  </div>
</template>

<style scoped>
.month-nav { display: flex; align-items: center; justify-content: center; gap: 16px; }
.btn-nav { width: 36px; height: 36px; border-radius: 50%; border: none; background: white; font-size: 22px; cursor: pointer; box-shadow: 0 1px 4px rgba(0,0,0,0.1); color: #667eea; line-height: 1; }
.btn-nav:active { transform: scale(0.95); }
.month-label { font-size: 16px; font-weight: 600; color: #333; }
</style>