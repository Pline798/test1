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

  const form = ref({
    amount: '',
    type: 'expense',
    category_id: '',
    description: '',
    date: new Date().toISOString().slice(0, 10),
  })

  const filteredTxns = computed(() => {
    if (!filterType.value) return transactions.value
    return transactions.value.filter(t => t.type === filterType.value)
  })

  const typeCats = computed(() => {
    return categories.value.filter(c => c.type === form.value.type)
  })

  async function loadData() {
    const [txns, cats] = await Promise.all([
      fetchTransactions(),
      fetchCategories(),
    ])
    transactions.value = txns
    categories.value = cats
  }

  async function loadTransactions() {
    transactions.value = await fetchTransactions()
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

  async function submit() {
    const data = {
      amount: parseFloat(form.value.amount),
      type: form.value.type,
      category_id: parseInt(form.value.category_id),
      description: form.value.description || '',
      date: form.value.date,
    }
    if (editingId.value) {
      await updateTransaction(editingId.value, data)
    } else {
      await createTransaction(data)
    }
    closeForm()
    await loadTransactions()
  }

  async function remove(id) {
    if (!confirm('确定删除这条记录吗？')) return
    await deleteTransaction(id)
    await loadTransactions()
  }

  return {
    transactions, categories, showForm, editingId, filterType, form,
    filteredTxns, typeCats,
    loadData, loadTransactions, openAdd, openEdit, closeForm, submit, remove,
  }
}