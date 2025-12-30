import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

// 路由配置
export const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: {
      title: '首页',
      keepAlive: true
    }
  },
  {
    path: '/search',
    name: 'Search',
    component: () => import('@/views/Search.vue'),
    meta: {
      title: '高级搜索',
      keepAlive: true
    }
  },
  {
    path: '/study/:id',
    name: 'StudyDetail',
    component: () => import('@/views/StudyDetail.vue'),
    meta: {
      title: '研究详情',
      keepAlive: false
    }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    meta: {
      title: '登录',
      requiresGuest: true
    }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/auth/Register.vue'),
    meta: {
      title: '注册',
      requiresGuest: true
    }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/user/Profile.vue'),
    meta: {
      title: '个人中心',
      requiresAuth: true
    }
  },
  {
    path: '/favorites',
    name: 'Favorites',
    component: () => import('@/views/user/Favorites.vue'),
    meta: {
      title: '我的收藏',
      requiresAuth: true
    }
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('@/views/user/History.vue'),
    meta: {
      title: '浏览历史',
      requiresAuth: true
    }
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('@/views/About.vue'),
    meta: {
      title: '关于我们',
      keepAlive: true
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: {
      title: '页面不存在'
    }
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 肿瘤治疗进展查询系统`
  }

  // 检查登录状态
  const token = localStorage.getItem('access_token')
  
  if (to.meta.requiresAuth && !token) {
    // 需要登录但未登录
    next({
      name: 'Login',
      query: { redirect: to.fullPath }
    })
  } else if (to.meta.requiresGuest && token) {
    // 需要未登录但已登录
    next({ name: 'Home' })
  } else {
    next()
  }
})

export default router