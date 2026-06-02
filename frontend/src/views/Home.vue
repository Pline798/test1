<script setup>
import { ref, onMounted, computed } from 'vue'
import { fetchStats, fetchTransactions, formatDate } from '../api'
import MonthPicker from '../components/MonthPicker.vue'

const stats = ref(null)
const recentTransactions = ref([])
const currentYear = ref(new Date().getFullYear())
const currentMonth = ref(new Date().getMonth() + 1)

const balance = computed(() => {
  if (!stats.value) return 0
  return (stats.value.income?.total || 0) - (stats.value.expense?.total || 0)
})

async function loadData() {
  const [s, txns] = await Promise.all([
    fetchStats({ year: currentYear.value, month: currentMonth.value }),
    fetchTransactions({ year: currentYear.value, month: currentMonth.value, limit: 5 }),
  ])
  stats.value = s
  recentTransactions.value = txns
}

function prevMonth() {
  if (currentMonth.value === 1) {
    currentMonth.value = 12
    currentYear.value--
  } else {
    currentMonth.value--
  }
}

function nextMonth() {
  if (currentMonth.value === 12) {
    currentMonth.value = 1
    currentYear.value++
  } else {
    currentMonth.value++
  }
}

onMounted(loadData)
</script>

<template>
  <div class="home">
    <MonthPicker :year="currentYear" :month="currentMonth" @prev="prevMonth" @next="nextMonth" />

    <div class="balance-card">
      <div class="balance-label">本月结余</div>
      <div class="balance-amount" :class="balance >= 0 ? 'positive' : 'negative'">
        ¥{{ balance.toFixed(2) }}
      </div>
      <div class="balance-detail">
        <span class="income">收入 ¥{{ (stats?.income?.total || 0).toFixed(2) }}</span>
        <span class="expense">支出 ¥{{ (stats?.expense?.total || 0).toFixed(2) }}</span>
      </div>
    </div>

    <div class="section">
      <h3 class="section-title">📈 本月分类统计</h3>
      <div class="category-stats">
        <div v-for="cat in (stats?.by_category || [])" :key="cat.category_id" class="cat-row">
          <span class="cat-icon" :style="{ background: cat.color + '20' }">{{ cat.icon }}</span>
          <span class="cat-name">{{ cat.category_name }}</span>
          <span class="cat-amount" :class="cat.type">¥{{ cat.total.toFixed(2) }}</span>
        </div>
        <div v-if="!stats?.by_category?.length" class="empty">暂无数据</div>
      </div>
    </div>

    <div class="section">
      <h3 class="section-title">📋 近期流水</h3>
      <div class="txn-list">
        <div v-for="txn in recentTransactions" :key="txn.id" class="txn-item">
          <span class="txn-icon" :style="{ background: (txn.category?.color || '#999') + '20' }">
            {{ txn.category?.icon || '📄' }}
          </span>
          <div class="txn-info">
            <div class="txn-category">{{ txn.category?.name || '未知' }}</div>
            <div class="txn-desc">{{ txn.description || formatDate(txn.date) }}</div>
          </div>
          <span class="txn-amount" :class="txn.type">
            {{ txn.type === 'income' ? '+' : '-' }}¥{{ txn.amount.toFixed(2) }}
          </span>
        </div>
        <div v-if="!recentTransactions.length" class="empty">暂无记录</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home { display: flex; flex-direction: column; gap: 16px; }
.balance-card { background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 16px; padding: 24px; color: white; text-align: center; }
.balance-label { font-size: 14px; opacity: 0.85; }
.balance-amount { font-size: 36px; font-weight: 700; margin: 8px 0; }
.balance-detail { display: flex; justify-content: space-around; font-size: 13px; margin-top: 12px; }
.balance-detail .income { color: #a8e6cf; }
.balance-detail .expense { color: #ffb3b3; }
.section { background: white; border-radius: 12px; padding: 16px; }
.section-title { font-size: 15px; margin-bottom: 12px; color: #333; }
.cat-row { display: flex; align-items: center; padding: 8px 0; border-bottom: 1px solid #f0f0f0; }
.cat-row:last-child { border-bottom: none; }
.cat-icon { width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 18px; margin-right: 12px; }
.cat-name { flex: 1; font-size: 14px; }
.cat-amount { font-size: 14px; font-weight: 600; }
.cat-amount.income { color: #67C23A; }
.cat-amount.expense { color: #F56C6C; }
.txn-list { display: flex; flex-direction: column; gap: 8px; }
.txn-item { display: flex; align-items: center; padding: 8px 0; border-bottom: 1px solid #f0f0f0; }
.txn-item:last-child { border-bottom: none; }
.txn-icon { width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 18px; margin-right: 12px; }
.txn-info { flex: 1; }
.txn-category { font-size: 14px; font-weight: 500; }
.txn-desc { font-size: 12px; color: #999; margin-top: 2px; }
.txn-amount { font-size: 15px; font-weight: 600; }
.txn-amount.income { color: #67C23A; }
.txn-amount.expense { color: #F56C6C; }
.empty { text-align: center; color: #ccc; padding: 20px; font-size: 14px; }
</style>