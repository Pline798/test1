import { createRouter, createWebHashHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Transactions from '../views/Transactions.vue'
import Categories from '../views/Categories.vue'
import AboutDoc from '../views/AboutDoc.vue'

const routes = [
  { path: '/', name: 'home', component: Home, meta: { title: '首页' } },
  { path: '/transactions', name: 'transactions', component: Transactions, meta: { title: '流水' } },
  { path: '/categories', name: 'categories', component: Categories, meta: { title: '分类管理' } },
  { path: '/about', name: 'about', component: AboutDoc, meta: { title: '项目文档' } },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

export default router