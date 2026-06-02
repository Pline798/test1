<script setup>
import NavBar from './components/NavBar.vue'
</script>

<template>
  <div class="app-container">
    <header class="app-header">
      <h1 class="app-title">📒 个人记账本</h1>
    </header>
    <main class="app-main">
      <router-view />
    </main>
    <NavBar />
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: #f5f7fa;
  color: #333;
  -webkit-font-smoothing: antialiased;
}

.app-container {
  max-width: 480px;
  margin: 0 auto;
  min-height: 100vh;
  background: #f5f7fa;
  position: relative;
  padding-bottom: 70px;
}

.app-header {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  padding: 20px 16px;
  text-align: center;
}

.app-title {
  font-size: 22px;
  font-weight: 600;
}

.app-main {
  padding: 16px;
}
</style>