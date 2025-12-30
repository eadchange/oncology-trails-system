<template>
  <div id="app" class="min-h-screen bg-background">
    <!-- 导航栏 -->
    <nav class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <!-- Logo和标题 -->
          <div class="flex items-center">
            <router-link to="/" class="flex items-center">
              <div class="w-8 h-8 bg-accent rounded-lg flex items-center justify-center mr-3">
                <span class="text-white font-bold text-sm">OT</span>
              </div>
              <h1 class="text-xl font-bold text-primary">肿瘤治疗进展查询系统</h1>
            </router-link>
          </div>
          
          <!-- 导航菜单 -->
          <div class="hidden md:flex items-center space-x-8">
            <router-link to="/" class="nav-link">首页</router-link>
            <router-link to="/search" class="nav-link">高级搜索</router-link>
            <router-link to="/about" class="nav-link">关于我们</router-link>
          </div>
          
          <!-- 用户菜单 -->
          <div class="flex items-center space-x-4">
            <template v-if="userStore.isLoggedIn">
              <el-dropdown @command="handleUserCommand">
                <span class="flex items-center cursor-pointer">
                  <el-avatar :size="32" class="mr-2">
                    {{ userStore.userInfo?.username?.charAt(0).toUpperCase() }}
                  </el-avatar>
                  <span class="text-sm text-gray-700">{{ userStore.userInfo?.username }}</span>
                  <el-icon class="ml-1"><ArrowDown /></el-icon>
                </span>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                    <el-dropdown-item command="favorites">我的收藏</el-dropdown-item>
                    <el-dropdown-item command="history">浏览历史</el-dropdown-item>
                    <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
            <template v-else>
              <router-link to="/login" class="btn btn-secondary">登录</router-link>
              <router-link to="/register" class="btn btn-primary">注册</router-link>
            </template>
          </div>
        </div>
      </div>
    </nav>
    
    <!-- 主内容区域 -->
    <main class="flex-1">
      <router-view />
    </main>
    
    <!-- 页脚 -->
    <footer class="bg-white border-t border-gray-200 mt-12">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="text-center">
          <p class="text-sm text-gray-600">
            © 2025 肿瘤治疗进展查询系统. 专业的肿瘤临床研究进展查询平台
          </p>
          <p class="text-xs text-gray-400 mt-2">
            数据来源：ClinicalTrials.gov, PubMed, ASCO, ESMO
          </p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'

const router = useRouter()
const userStore = useUserStore()

// 处理用户菜单命令
const handleUserCommand = (command: string) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'favorites':
      router.push('/favorites')
      break
    case 'history':
      router.push('/history')
      break
    case 'logout':
      handleLogout()
      break
  }
}

// 处理退出登录
const handleLogout = async () => {
  try {
    await userStore.logout()
    ElMessage.success('退出登录成功')
    router.push('/')
  } catch (error) {
    ElMessage.error('退出登录失败')
  }
}

// 组件挂载时检查登录状态
onMounted(() => {
  userStore.checkLoginStatus()
})
</script>

<style scoped>
.nav-link {
  @apply text-gray-600 hover:text-accent px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200;
}

.router-link-active.nav-link {
  @apply text-accent bg-accent/10;
}
</style>