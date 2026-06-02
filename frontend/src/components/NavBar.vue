<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()

const tabs = [
  { name: 'home', path: '/', label: '首页', icon: '📊' },
  { name: 'transactions', path: '/transactions', label: '流水', icon: '📋' },
  { name: 'categories', path: '/categories', label: '分类', icon: '🏷️' },
  { name: 'about', path: '/about', label: '文档', icon: '📖' },
]
</script>

<template>
  <nav class="nav-bar">
    <router-link
      v-for="tab in tabs"
      :key="tab.name"
      :to="tab.path"
      class="nav-item"
      :class="{ active: route.name === tab.name }"
    >
      <span class="nav-icon">{{ tab.icon }}</span>
      <span class="nav-label">{{ tab.label }}</span>
    </router-link>
  </nav>
</template>

<style scoped>
.nav-bar {
  position: fixed;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  max-width: 480px;
  width: 100%;
  display: flex;
  background: white;
  border-top: 1px solid #eee;
  z-index: 100;
}

.nav-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 0 10px;
  text-decoration: none;
  color: #999;
  transition: color 0.2s;
}

.nav-item.active {
  color: #667eea;
}

.nav-icon {
  font-size: 22px;
  line-height: 1;
}

.nav-label {
  font-size: 12px;
  margin-top: 2px;
}
</style>