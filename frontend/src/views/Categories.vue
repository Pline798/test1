<script setup>
import { onMounted } from 'vue'
import { useCategories } from '../composables/useCategories'
import CategoryForm from '../components/CategoryForm.vue'

const {
  categories, showForm, editingId, filterType, form,
  iconOptions, colorOptions,
  loadAll, openAdd, openEdit, closeForm, submit, remove,
} = useCategories()

onMounted(loadAll)
</script>

<template>
  <div class="categories">
    <div class="tab-bar">
      <button :class="['tab', { active: filterType === 'expense' }]" @click="filterType = 'expense'">支出分类</button>
      <button :class="['tab', { active: filterType === 'income' }]" @click="filterType = 'income'">收入分类</button>
    </div>

    <div class="cat-grid">
      <div v-for="cat in (categories[filterType] || [])" :key="cat.id" class="cat-card" :style="{ borderTopColor: cat.color }">
        <span class="cat-icon" :style="{ background: cat.color + '20' }">{{ cat.icon }}</span>
        <span class="cat-name">{{ cat.name }}</span>
        <div class="cat-actions">
          <button class="mini-btn" @click="openEdit(cat)">✏️</button>
          <button class="mini-btn" @click="remove(cat.id)">🗑️</button>
        </div>
      </div>
      <div class="cat-card add-card" @click="openAdd(filterType)">
        <span class="add-icon">+</span>
        <span class="add-text">添加分类</span>
      </div>
    </div>

    <CategoryForm
      :show="showForm"
      :editing-id="editingId"
      :form="form"
      :icon-options="iconOptions"
      :color-options="colorOptions"
      @close="closeForm"
      @submit="submit"
    />
  </div>
</template>

<style scoped>
.categories { display: flex; flex-direction: column; gap: 12px; }
.tab-bar { display: flex; gap: 8px; }
.tab { flex: 1; padding: 10px; border: 1px solid #e0e0e0; border-radius: 8px; background: white; font-size: 14px; cursor: pointer; color: #666; }
.tab.active { background: #667eea; color: white; border-color: #667eea; }
.cat-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
.cat-card { background: white; border-radius: 12px; padding: 16px 8px; display: flex; flex-direction: column; align-items: center; gap: 6px; border-top: 3px solid transparent; position: relative; }
.cat-icon { width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; }
.cat-name { font-size: 13px; color: #333; }
.cat-actions { display: flex; gap: 4px; }
.mini-btn { background: none; border: none; cursor: pointer; font-size: 12px; padding: 2px; }
.add-card { border: 2px dashed #ddd; cursor: pointer; justify-content: center; transition: border-color 0.2s; }
.add-card:hover { border-color: #667eea; }
.add-icon { font-size: 28px; color: #ccc; line-height: 1; }
.add-text { font-size: 12px; color: #999; }
</style>