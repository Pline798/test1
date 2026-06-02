import { ref, computed } from 'vue'
import {
  fetchTransactions, createTransaction, updateTransaction, deleteTransaction,
  fetchCategories,
} from '../api'

export function useTransactions() {
  const transactions = ref([])
  const categories = ref([])
  const showForm = ref(false)
  const editingId = ref(null)
  const filterType = ref('')
  const loading = ref(false)

  const searchKeyword = ref('')
  const amountMin = ref('')
  const amountMax = ref('')

  const form = ref({
    amount: '',
    type: 'expense',
    category_id: '',
    description: '',
    date: new Date().toISOString().slice(0, 10),
  })

  const filteredTxns = computed(() => {
    let result = transactions.value
    if (filterType.value) {
      result = result.filter(t => t.type === filterType.value)
    }
    if (searchKeyword.value) {
      const kw = searchKeyword.value.toLowerCase()
      result = result.filter(t => (t.description || '').toLowerCase().includes(kw))
    }
    const minVal = parseFloat(amountMin.value)
    const maxVal = parseFloat(amountMax.value)
    if (!isNaN(minVal)) {
      result = result.filter(t => t.amount >= minVal)
    }
    if (!isNaN(maxVal)) {
      result = result.filter(t => t.amount <= maxVal)
    }
    return result
  })

  const typeCats = computed(() => {
    return categories.value.filter(c => c.type === form.value.type)
  })

  async function loadData() {
    loading.value = true
    try {
      const params = {}
      if (filterType.value) params.type = filterType.value
      const [txns, cats] = await Promise.all([
        fetchTransactions(params),
        fetchCategories(),
      ])
      transactions.value = txns
      categories.value = cats
    } catch (e) {
      // 错误由拦截器处理
    } finally {
      loading.value = false
    }
  }

  async function loadTransactions() {
    try {
      const params = {}
      if (filterType.value) params.type = filterType.value
      transactions.value = await fetchTransactions(params)
    } catch (e) {
      // 错误由拦截器处理
    }
  }

  function openAdd(type) {
    editingId.value = null
    form.value = { amount: '', type, category_id: '', description: '', date: new Date().toISOString().slice(0, 10) }
    showForm.value = true
  }

  function openEdit(txn) {
    editingId.value = txn.id
    form.value = {
      amount: String(txn.amount),
      type: txn.type,
      category_id: txn.category_id,
      description: txn.description || '',
      date: txn.date,
    }
    showForm.value = true
  }

  function closeForm() {
    showForm.value = false
    editingId.value = null
  }

  function clearSearch() {
    searchKeyword.value = ''
    amountMin.value = ''
    amountMax.value = ''
  }

  async function submit() {
    const data = {
      amount: parseFloat(form.value.amount),
      type: form.value.type,
      category_id: parseInt(form.value.category_id),
      description: form.value.description || '',
      date: form.value.date,
    }
    try {
      if (editingId.value) {
        await updateTransaction(editingId.value, data)
      } else {
        await createTransaction(data)
      }
      closeForm()
      await loadTransactions()
    } catch (e) {
      // 错误由拦截器处理
    }
  }

  async function remove(id) {
    if (!confirm('确定删除这条记录吗？')) return
    try {
      await deleteTransaction(id)
      await loadTransactions()
    } catch (e) {
      // 错误由拦截器处理
    }
  }

  return {
    transactions, categories, showForm, editingId, filterType, form, loading,
    filteredTxns, typeCats, searchKeyword, amountMin, amountMax, clearSearch,
    loadData, loadTransactions, openAdd, openEdit, closeForm, submit, remove,
  }
}