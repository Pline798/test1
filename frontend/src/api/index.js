import axios from 'axios'
import dayjs from 'dayjs'

const http = axios.create({ baseURL: '/api' })

// 全局错误处理
http.interceptors.response.use(
  res => res,
  error => {
    const msg = error.response?.data?.detail || error.message || '网络请求失败'
    console.error('[API Error]', msg)
    alert('操作失败：' + msg)
    return Promise.reject(error)
  },
)

export async function fetchCategories(type) {
  const params = type ? { type } : {}
  const res = await http.get('/categories', { params })
  return res.data
}

export async function createCategory(data) {
  const res = await http.post('/categories', data)
  return res.data
}

export async function updateCategory(id, data) {
  const res = await http.put(`/categories/${id}`, data)
  return res.data
}

export async function deleteCategory(id) {
  const res = await http.delete(`/categories/${id}`)
  return res.data
}

export async function fetchTransactions(params) {
  const res = await http.get('/transactions', { params })
  return res.data
}

export async function createTransaction(data) {
  const res = await http.post('/transactions', data)
  return res.data
}

export async function updateTransaction(id, data) {
  const res = await http.put(`/transactions/${id}`, data)
  return res.data
}

export async function deleteTransaction(id) {
  const res = await http.delete(`/transactions/${id}`)
  return res.data
}

export async function fetchStats(params) {
  const res = await http.get('/stats', { params })
  return res.data
}

export function formatDate(d) {
  return dayjs(d).format('YYYY-MM-DD')
}