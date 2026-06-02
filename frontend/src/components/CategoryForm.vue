<script setup>
defineProps({ show: Boolean, editingId: Number, form: Object, iconOptions: Array, colorOptions: Array })
const emit = defineEmits(['close', 'submit'])
</script>

<template>
  <div v-if="show" class="modal-overlay" @click.self="emit('close')">
    <div class="modal">
      <h3>{{ editingId ? '编辑' : '新增' }}分类</h3>
      <div class="form-group">
        <label>名称</label>
        <input v-model="form.name" type="text" placeholder="分类名称" class="input" />
      </div>
      <div class="form-group">
        <label>图标</label>
        <div class="icon-grid">
          <button
            v-for="icon in iconOptions" :key="icon"
            :class="['icon-btn', { active: form.icon === icon }]"
            @click="form.icon = icon"
          >{{ icon }}</button>
        </div>
      </div>
      <div class="form-group">
        <label>颜色</label>
        <div class="color-grid">
          <button
            v-for="c in colorOptions" :key="c"
            :class="['color-btn', { active: form.color === c }]"
            :style="{ background: c }"
            @click="form.color = c"
          ></button>
        </div>
      </div>
      <div class="form-actions">
        <button class="btn btn-cancel" @click="emit('close')">取消</button>
        <button class="btn btn-submit" @click="emit('submit')" :disabled="!form.name">确定</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.4);
  display: flex; align-items: center; justify-content: center; z-index: 200;
}
.modal { background: white; border-radius: 16px; padding: 24px; width: 90%; max-width: 400px; max-height: 80vh; overflow-y: auto; }
.modal h3 { margin-bottom: 16px; font-size: 18px; }
.form-group { margin-bottom: 14px; }
.form-group label { display: block; font-size: 13px; color: #666; margin-bottom: 6px; }
.input { width: 100%; padding: 10px 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; outline: none; box-sizing: border-box; }
.input:focus { border-color: #667eea; }
.icon-grid { display: flex; flex-wrap: wrap; gap: 6px; }
.icon-btn { width: 38px; height: 38px; border: 2px solid transparent; border-radius: 8px; font-size: 18px; cursor: pointer; background: #f5f7fa; display: flex; align-items: center; justify-content: center; }
.icon-btn.active { border-color: #667eea; background: #667eea20; }
.color-grid { display: flex; flex-wrap: wrap; gap: 8px; }
.color-btn { width: 32px; height: 32px; border-radius: 50%; border: 3px solid transparent; cursor: pointer; }
.color-btn.active { border-color: #333; }
.form-actions { display: flex; gap: 10px; margin-top: 20px; }
.form-actions .btn { flex: 1; padding: 10px; border: none; border-radius: 8px; font-size: 14px; cursor: pointer; font-weight: 500; }
.btn-cancel { background: #f0f0f0; color: #666; }
.btn-submit { background: #667eea; color: white; }
.btn-submit:disabled { opacity: 0.5; cursor: not-allowed; }
</style>