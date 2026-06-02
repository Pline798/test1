<script setup>
defineProps({ show: Boolean, editingId: Number, form: Object, typeCats: Array })
const emit = defineEmits(['close', 'submit'])
</script>

<template>
  <div v-if="show" class="modal-overlay" @click.self="emit('close')">
    <div class="modal">
      <h3>{{ editingId ? '编辑' : '新增' }}{{ form.type === 'income' ? '收入' : '支出' }}</h3>
      <div class="form-group">
        <label>金额</label>
        <input v-model.number="form.amount" type="number" step="0.01" min="0.01" placeholder="0.00" class="input" />
      </div>
      <div class="form-group">
        <label>分类</label>
        <select v-model="form.category_id" class="input">
          <option value="" disabled>请选择</option>
          <option v-for="cat in typeCats" :key="cat.id" :value="cat.id">{{ cat.icon }} {{ cat.name }}</option>
        </select>
      </div>
      <div class="form-group">
        <label>日期</label>
        <input v-model="form.date" type="date" class="input" />
      </div>
      <div class="form-group">
        <label>备注</label>
        <input v-model="form.description" type="text" placeholder="可选" class="input" />
      </div>
      <div class="form-actions">
        <button class="btn btn-cancel" @click="emit('close')">取消</button>
        <button class="btn btn-submit" @click="emit('submit')" :disabled="!form.amount || !form.category_id">
          {{ editingId ? '保存' : '添加' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.4);
  display: flex; align-items: center; justify-content: center; z-index: 200;
}
.modal { background: white; border-radius: 16px; padding: 24px; width: 90%; max-width: 400px; }
.modal h3 { margin-bottom: 16px; font-size: 18px; }
.form-group { margin-bottom: 14px; }
.form-group label { display: block; font-size: 13px; color: #666; margin-bottom: 4px; }
.input { width: 100%; padding: 10px 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; outline: none; box-sizing: border-box; }
.input:focus { border-color: #667eea; }
.form-actions { display: flex; gap: 10px; margin-top: 20px; }
.form-actions .btn { flex: 1; padding: 10px; border: none; border-radius: 8px; font-size: 14px; cursor: pointer; font-weight: 500; }
.btn-cancel { background: #f0f0f0; color: #666; }
.btn-submit { background: #667eea; color: white; }
.btn-submit:disabled { opacity: 0.5; cursor: not-allowed; }
</style>