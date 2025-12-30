import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import { createRouter, createWebHistory } from 'vue-router'
import { createI18n } from 'vue-i18n'

import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import './assets/styles/main.css'

import App from './App.vue'
import { routes } from './router'

// 创建Pinia
const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

// 创建路由
const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 创建应用
const app = createApp(App)

// 注册Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 使用插件
app.use(pinia)
app.use(router)
app.use(ElementPlus)

// 挂载应用
app.mount('#app')