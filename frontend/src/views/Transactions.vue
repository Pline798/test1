<script setup>
import { onMounted } from 'vue'
import { useTransactions } from '../composables/useTransactions'
import TransactionForm from '../components/TransactionForm.vue'

const {
  transactions, categories, showForm, editingId, filterType, form,
  filteredTxns, typeCats,
  loadData, loadTransactions, openAdd, openEdit, closeForm, submit, remove,
} = useTransactions()

onMounted(loadData)
</script>

<template>
  <div class="transactions">
    <div class="toolbar">
      <div class="filter-tabs">
        <button :class="['filter-btn', { active: filterType === '' }]" @click="filterType = ''">全部</button>
        <button :class="['filter-btn', { active: filterType === 'expense' }]" @click="filterType = 'expense'">支出</button>
        <button :class="['filter-btn', { active: filterType === 'income' }]" @click="filterType = 'income'">收入</button>
      </div>
      <div class="add-btns">
        <button class="btn btn-expense" @click="openAdd('expense')">+ 支出</button>
        <button class="btn btn-income" @click="openAdd('income')">+ 收入</button>
      </div>
    </div>

    <div class="list">
      <div v-for="txn in filteredTxns" :key="txn.id" class="card">
        <div class="card-left">
          <span class="card-icon" :style="{ background: (txn.category?.color || '#999') + '20' }">
            {{ txn.category?.icon || '📄' }}
          </span>
          <div class="card-info">
            <div class="card-category">{{ txn.category?.name || '未知' }}</div>
            <div class="card-desc">{{ txn.description || '无备注' }}</div>
          </div>
        </div>
        <div class="card-right">
          <div class="card-amount" :class="txn.type">
            {{ txn.type === 'income' ? '+' : '-' }}¥{{ txn.amount.toFixed(2) }}
          </div>
          <div class="card-date">{{ txn.date }}</div>
          <div class="card-actions">
            <button class="action-btn" @click="openEdit(txn)">✏️</button>
            <button class="action-btn" @click="remove(txn.id)">🗑️</button>
          </div>
        </div>
      </div>
      <div v-if="!filteredTxns.length" class="empty">暂无记录</div>
    </div>

    <TransactionForm
      :show="showForm"
      :editing-id="editingId"
      :form="form"
      :type-cats="typeCats"
      @close="closeForm"
      @submit="submit"
    />
  </div>
</template>

<style scoped>
.transactions { display: flex; flex-direction: column; gap: 12px; }
.toolbar { display: flex; flex-direction: column; gap: 10px; }
.filter-tabs { display: flex; gap: 8px; }
.filter-btn { flex: 1; padding: 8px; border: 1px solid #e0e0e0; border-radius: 8px; background: white; font-size: 13px; cursor: pointer; color: #666; }
.filter-btn.active { background: #667eea; color: white; border-color: #667eea; }
.add-btns { display: flex; gap: 8px; }
.btn { flex: 1; padding: 10px; border: none; border-radius: 8px; font-size: 14px; cursor: pointer; font-weight: 500; }
.btn-expense { background: #F56C6C; color: white; }
.btn-income { background: #67C23A; color: white; }
.list { display: flex; flex-direction: column; gap: 8px; }
.card { background: white; border-radius: 12px; padding: 12px 16px; display: flex; justify-content: space-between; align-items: center; }
.card-left { display: flex; align-items: center; gap: 10px; }
.card-icon { width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; }
.card-category { font-size: 14px; font-weight: 500; }
.card-desc { font-size: 12px; color: #999; margin-top: 2px; }
.card-right { text-align: right; }
.card-amount { font-size: 16px; font-weight: 700; }
.card-amount.income { color: #67C23A; }
.card-amount.expense { color: #F56C6C; }
.card-date { font-size: 11px; color: #bbb; margin-top: 2px; }
.card-actions { margin-top: 4px; display: flex; gap: 4px; justify-content: flex-end; }
.action-btn { background: none; border: none; cursor: pointer; font-size: 14px; padding: 2px; }
.empty { text-align: center; color: #ccc; padding: 40px; font-size: 14px; }
</style>