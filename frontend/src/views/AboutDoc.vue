<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { marked } from 'marked'

const router = useRouter()
const content = ref('')
const loading = ref(true)
const currentDoc = ref('readme')

const docs = {
  readme: { file: '/docs/README.md', label: '项目文档', icon: '📖' },
  implement: { file: '/docs/IMPLEMENTATION.md', label: '实现文档', icon: '📝' },
}

async function loadDoc(name) {
  loading.value = true
  const doc = docs[name]
  if (!doc) return
  try {
    const resp = await fetch(doc.file)
    if (!resp.ok) throw new Error('Not found')
    const md = await resp.text()
    content.value = await marked.parse(md)
  } catch (e) {
    content.value = '<p style="color:red">文档加载失败，请刷新重试</p>'
  } finally {
    loading.value = false
  }
}

onMounted(() => loadDoc(currentDoc.value))

function switchDoc(name) {
  currentDoc.value = name
  loadDoc(name)
}

function goBack() {
  router.back()
}
</script>

<template>
  <div class="doc-page">
    <header class="doc-header">
      <button class="back-btn" @click="goBack">← 返回</button>
      <h2>{{ docs[currentDoc]?.label || '文档' }}</h2>
      <a :href="docs[currentDoc]?.file" download class="download-btn" title="下载文档">⬇</a>
    </header>
    <div class="doc-tabs">
      <button
        v-for="(doc, key) in docs"
        :key="key"
        :class="['tab-btn', { active: currentDoc === key }]"
        @click="switchDoc(key)"
      >
        {{ doc.icon }} {{ doc.label }}
      </button>
    </div>
    <div class="doc-body">
      <div v-if="loading" class="doc-loading">加载中...</div>
      <div v-else class="doc-content" v-html="content"></div>
    </div>
  </div>
</template>

<style scoped>
.doc-page {
  min-height: calc(100vh - 50px);
  display: flex;
  flex-direction: column;
}

.doc-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: white;
  border-radius: 12px;
  margin-bottom: 10px;
}

.back-btn {
  background: none;
  border: none;
  font-size: 15px;
  color: #667eea;
  cursor: pointer;
  padding: 4px 8px;
}

.doc-header h2 {
  font-size: 17px;
  color: #333;
}

.download-btn {
  font-size: 18px;
  text-decoration: none;
  color: #667eea;
  padding: 4px 8px;
}

.doc-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 10px;
}

.tab-btn {
  flex: 1;
  padding: 10px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: white;
  font-size: 14px;
  cursor: pointer;
  color: #666;
  transition: all 0.2s;
}

.tab-btn.active {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

.doc-body {
  background: white;
  border-radius: 12px;
  padding: 24px;
  flex: 1;
  overflow-y: auto;
}

.doc-loading {
  text-align: center;
  color: #999;
  padding: 40px;
}

.doc-content {
  font-size: 15px;
  line-height: 1.8;
  color: #333;
}

.doc-content :deep(h1) {
  font-size: 24px;
  margin: 0 0 16px;
  padding-bottom: 12px;
  border-bottom: 3px solid #667eea;
  color: #222;
}

.doc-content :deep(h2) {
  font-size: 20px;
  margin: 28px 0 12px;
  padding-bottom: 8px;
  border-bottom: 2px solid #e8e8e8;
  color: #333;
}

.doc-content :deep(h3) {
  font-size: 17px;
  margin: 24px 0 10px;
  color: #444;
}

.doc-content :deep(p) {
  margin: 10px 0;
  text-align: justify;
}

.doc-content :deep(ul),
.doc-content :deep(ol) {
  padding-left: 24px;
  margin: 10px 0;
}

.doc-content :deep(li) {
  margin: 6px 0;
}

.doc-content :deep(code) {
  background: #f0f2f5;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 14px;
  color: #d63384;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
}

.doc-content :deep(pre) {
  background: #1e1e2e;
  color: #cdd6f4;
  padding: 18px 20px;
  border-radius: 10px;
  overflow-x: auto;
  margin: 14px 0;
  font-size: 14px;
  line-height: 1.6;
}

.doc-content :deep(pre code) {
  background: none;
  color: inherit;
  padding: 0;
  font-size: inherit;
}

.doc-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 14px 0;
  font-size: 14px;
}

.doc-content :deep(th),
.doc-content :deep(td) {
  border: 1px solid #e0e0e0;
  padding: 10px 14px;
  text-align: left;
}

.doc-content :deep(th) {
  background: #f5f7fa;
  font-weight: 600;
  color: #444;
}

.doc-content :deep(tr:nth-child(even)) {
  background: #fafbfc;
}

.doc-content :deep(blockquote) {
  border-left: 4px solid #667eea;
  padding: 10px 18px;
  margin: 14px 0;
  background: #f5f7fa;
  border-radius: 0 8px 8px 0;
  color: #555;
}

.doc-content :deep(hr) {
  border: none;
  border-top: 2px solid #eee;
  margin: 24px 0;
}

.doc-content :deep(a) {
  color: #667eea;
  text-decoration: none;
}

.doc-content :deep(a:hover) {
  text-decoration: underline;
}

.doc-content :deep(strong) {
  color: #222;
}

.doc-content :deep(img) {
  max-width: 100%;
  border-radius: 8px;
}
</style>