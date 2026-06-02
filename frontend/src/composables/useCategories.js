import { ref } from 'vue'
import { fetchCategories, createCategory, updateCategory, deleteCategory } from '../api'

export function useCategories() {
  const categories = ref([])
  const showForm = ref(false)
  const editingId = ref(null)
  const filterType = ref('expense')

  const form = ref({
    name: '',
    type: 'expense',
    icon: '📁',
    color: '#409EFF',
  })

  const iconOptions = [
    '💰','💼','📈','🧧','💵','🍜','🚌','🛒','🏠','🎮',
    '💊','📚','📱','📦','🎬','☕','🐱','🐶','💻','🏋️',
    '🎨','✈️','🎂','💄','📷','🎵','🌴','🎁','🔧','📄',
  ]

  const colorOptions = [
    '#F56C6C','#E6A23C','#67C23A','#409EFF','#9B59B6',
    '#1ABC9C','#E74C3C','#3498DB','#95A5A6','#2ECC71',
  ]

  async function loadAll() {
    const cats = await fetchCategories()
    const income = cats.filter(c => c.type === 'income')
    const expense = cats.filter(c => c.type === 'expense')
    categories.value = { income, expense }
  }

  function openAdd(type) {
    editingId.value = null
    form.value = { name: '', type, icon: '📁', color: '#409EFF' }
    showForm.value = true
  }

  function openEdit(cat) {
    editingId.value = cat.id
    form.value = { name: cat.name, type: cat.type, icon: cat.icon, color: cat.color }
    showForm.value = true
  }

  function closeForm() {
    showForm.value = false
    editingId.value = null
  }

  async function submit() {
    if (editingId.value) {
      await updateCategory(editingId.value, form.value)
    } else {
      await createCategory(form.value)
    }
    closeForm()
    await loadAll()
  }

  async function remove(id) {
    if (!confirm('删除分类会同时删除该分类下的所有流水记录，确定吗？')) return
    await deleteCategory(id)
    await loadAll()
  }

  return {
    categories, showForm, editingId, filterType, form,
    iconOptions, colorOptions,
    loadAll, openAdd, openEdit, closeForm, submit, remove,
  }
}