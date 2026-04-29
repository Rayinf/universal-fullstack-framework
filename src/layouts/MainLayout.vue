<template>
  <el-container class="layout-container">
    <!-- 顶部 LOGO 和操作区域 -->
    <el-header class="layout-header">
      <div class="header-content">
        <div class="logo-area">
          <img
            src="@/assets/单LOGO.png"
            alt="系统LOGO"
            class="logo-img"
            v-if="!isMobile || sidebarCollapsed"
          />
          <span class="system-title"
            >{{ systemConfigStore.configData.systemName || 'MES管理系统' }}
            <span v-if="systemConfigStore.configData.companyName" class="tenant-subtitle"
              >- {{ systemConfigStore.configData.companyName }}</span
            ></span
          >
        </div>
        <div class="header-actions">
          <el-tooltip content="全屏" placement="bottom" v-if="!isMobile">
            <el-icon class="action-icon" @click="toggleFullScreen">
              <FullScreen />
            </el-icon>
          </el-tooltip>

          <NotificationBell />

          <el-dropdown @command="handleUserCommand">
            <span class="user-avatar-container">
              <el-avatar size="small" :icon="UserFilled" />
              <span class="username">{{ userStore.currentUser?.name || '当前用户' }}</span>
              <el-icon class="el-icon--right"><arrow-down /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          <el-icon
            class="action-icon mobile-menu-button"
            @click="toggleSidebarDrawer"
            v-if="isMobile"
          >
            <Menu />
          </el-icon>
        </div>
      </div>
    </el-header>

    <el-container class="main-body-container">
      <!-- 左侧菜单 -->
      <el-aside :width="sidebarWidth" class="layout-sidebar" v-if="!isMobile">
        <el-scrollbar>
          <el-menu
            :default-active="activeMenu"
            class="el-menu-vertical-custom"
            :collapse="sidebarCollapsed"
            :collapse-transition="false"
            router
            unique-opened
          >
            <template v-for="menu in sidebarMenus" :key="menu.id">
              <el-menu-item v-if="!menu.children" :index="menu.path || `/${menu.id}`">
                <el-icon><component :is="getIconComponent(menu.icon)" /></el-icon>
                <template #title>{{ menu.title }}</template>
              </el-menu-item>

              <el-sub-menu v-else :index="menu.id">
                <template #title>
                  <el-icon><component :is="getIconComponent(menu.icon)" /></el-icon>
                  <span>{{ menu.title }}</span>
                </template>

                <template v-for="subMenu in menu.children" :key="subMenu?.id">
                  <el-menu-item
                    v-if="subMenu && !subMenu.children"
                    :index="subMenu.path || `/${subMenu.id}`"
                  >
                    {{ subMenu.title }}
                  </el-menu-item>

                  <el-sub-menu v-else-if="subMenu && subMenu.children" :index="subMenu.id">
                    <template #title>{{ subMenu.title }}</template>
                    <template v-for="thirdMenu in subMenu.children" :key="thirdMenu?.id">
                      <el-menu-item v-if="thirdMenu" :index="thirdMenu.path || `/${thirdMenu.id}`">
                        {{ thirdMenu.title }}
                      </el-menu-item>
                    </template>
                  </el-sub-menu>
                </template>
              </el-sub-menu>
            </template>
          </el-menu>
        </el-scrollbar>
        <div class="sidebar-collapse-button" @click="toggleSidebarCollapse" v-if="!isMobile">
          <el-icon>
            <component :is="sidebarCollapsed ? Expand : Fold" />
          </el-icon>
        </div>
      </el-aside>

      <!-- 移动端抽屉菜单 -->
      <el-drawer
        v-model="sidebarDrawerVisible"
        title="导航菜单"
        direction="ltr"
        :with-header="true"
        size="220px"
        v-if="isMobile"
      >
        <el-scrollbar>
          <el-menu
            :default-active="activeMenu"
            class="el-menu-vertical-custom"
            router
            unique-opened
            @select="handleMobileMenuSelect"
          >
            <template v-for="menu in sidebarMenus" :key="menu.id">
              <el-menu-item v-if="!menu.children" :index="menu.path || `/${menu.id}`">
                <el-icon><component :is="getIconComponent(menu.icon)" /></el-icon>
                <template #title>{{ menu.title }}</template>
              </el-menu-item>

              <el-sub-menu v-else :index="menu.id">
                <template #title>
                  <el-icon><component :is="getIconComponent(menu.icon)" /></el-icon>
                  <span>{{ menu.title }}</span>
                </template>

                <template v-for="subMenu in menu.children" :key="subMenu?.id">
                  <el-menu-item
                    v-if="subMenu && !subMenu.children"
                    :index="subMenu.path || `/${subMenu.id}`"
                  >
                    {{ subMenu.title }}
                  </el-menu-item>

                  <el-sub-menu v-else-if="subMenu && subMenu.children" :index="subMenu.id">
                    <template #title>{{ subMenu.title }}</template>
                    <template v-for="thirdMenu in subMenu.children" :key="thirdMenu?.id">
                      <el-menu-item v-if="thirdMenu" :index="thirdMenu.path || `/${thirdMenu.id}`">
                        {{ thirdMenu.title }}
                      </el-menu-item>
                    </template>
                  </el-sub-menu>
                </template>
              </el-sub-menu>
            </template>
          </el-menu>
        </el-scrollbar>
      </el-drawer>

      <!-- 右侧内容区 -->
      <el-main class="layout-main-content">
        <el-scrollbar class="main-content-scrollbar">
          <RouterView />
        </el-scrollbar>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, type Component } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Fold,
  Expand,
  FullScreen,
  UserFilled,
  ArrowDown,
  Menu,
} from '@element-plus/icons-vue'
import { useUserStore } from '../stores/userStore'
import { useSystemConfigStore } from '@/stores/system/systemConfig'
import { useMenuStore } from '@/stores/menuStore'
import { mesMenuConfig } from '@/config/menuConfig'
import { isFrameworkEnabledRoute } from '@/config/frameworkConfig'
import type { NavMenuItem } from '@/stores/menuStore'
import NotificationBell from '@/components/common/NotificationBell.vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const systemConfigStore = useSystemConfigStore()
const menuStore = useMenuStore()

const normalizePath = (path?: string): string => {
  if (!path) return ''
  return path.startsWith('/') ? path : `/${path}`
}

const isHomeMenu = (menu: NavMenuItem): boolean => {
  return menu.id === 'home' || normalizePath(menu.path) === '/'
}

const isFrameworkPath = (path?: string): boolean => {
  const normalizedPath = normalizePath(path)
  return !!normalizedPath && isFrameworkEnabledRoute(normalizedPath)
}

const filterFrameworkMenus = (menus: NavMenuItem[]): NavMenuItem[] => {
  const result: NavMenuItem[] = []
  const seen = new Set<string>()

  for (const menu of menus) {
    const key = `${menu.id}::${normalizePath(menu.path)}`
    if (seen.has(key)) continue
    seen.add(key)

    if (isHomeMenu(menu)) {
      result.push({ ...menu, children: undefined })
      continue
    }

    const filteredChildren = menu.children?.length ? filterFrameworkMenus(menu.children) : undefined
    const ownFrameworkMenu = isFrameworkPath(menu.path)
    const hasFrameworkChildren = !!filteredChildren && filteredChildren.length > 0

    if (ownFrameworkMenu || hasFrameworkChildren) {
      result.push({
        ...menu,
        children: hasFrameworkChildren ? filteredChildren : undefined,
      })
    }
  }

  return result
}

const buildFallbackMenus = (): NavMenuItem[] => {
  return mesMenuConfig
    .filter((menu) => !menu.hidden)
    .map((menu) => ({
      id: menu.id,
      title: menu.title,
      path: menu.path,
      icon: menu.icon,
      children: menu.children
        ?.filter((child) => !child.hidden)
        .map((child) => ({
          id: child.id,
          title: child.title,
          path: child.path,
          icon: child.icon,
          children: child.children
            ?.filter((grandChild) => !grandChild.hidden)
            .map((grandChild) => ({
              id: grandChild.id,
              title: grandChild.title,
              path: grandChild.path,
              icon: grandChild.icon,
            })),
        })),
    }))
}

const hasFrameworkMenu = (menus: NavMenuItem[]): boolean => {
  return menus.some((menu) => {
    if (isFrameworkPath(menu.path)) return true
    return !!menu.children?.length && hasFrameworkMenu(menu.children)
  })
}

// 实际渲染用的菜单：后端优先，按已启用框架模块渲染
const sidebarMenus = computed<NavMenuItem[]>(() => {
  const sourceMenus = menuStore.navMenus.length > 0 ? menuStore.navMenus : buildFallbackMenus()
  const frameworkMenus = filterFrameworkMenus(sourceMenus)
  return hasFrameworkMenu(frameworkMenus) ? frameworkMenus : buildFallbackMenus()
})

const sidebarCollapsed = ref(false)
const sidebarDrawerVisible = ref(false)
const isMobile = ref(window.innerWidth < 768)

const sidebarWidth = computed(() => (sidebarCollapsed.value ? '64px' : '220px'))
const activeMenu = computed(() => route.path)

const getIconComponent = (iconName?: string) => {
  return iconName || 'Setting'
}

const toggleSidebarCollapse = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

const toggleSidebarDrawer = () => {
  sidebarDrawerVisible.value = !sidebarDrawerVisible.value
}

const handleResize = () => {
  isMobile.value = window.innerWidth < 768
  if (!isMobile.value && sidebarDrawerVisible.value) {
    sidebarDrawerVisible.value = false
  }
  if (isMobile.value) {
    sidebarCollapsed.value = false
  }
}

const toggleFullScreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
  } else {
    if (document.exitFullscreen) {
      document.exitFullscreen()
    }
  }
}

const handleUserCommand = async (command: string) => {
  if (command === 'logout') {
    try {
      await userStore.logout()
      router.push({ name: 'Login' })
    } catch (error) {
      console.error('登出失败:', error)
    }
  } else if (command === 'profile') {
    router.push({ path: '/system/profile' })
  }
}

const handleMobileMenuSelect = () => {
  sidebarDrawerVisible.value = false
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
  handleResize()

  if (!userStore.tenantName) {
    userStore.fetchTenantName()
  }

  // 获取系统配置
  if (!systemConfigStore.hasLoaded) {
    systemConfigStore.initialize()
  }

  // 从后端加载菜单树
  if (!menuStore.loaded) {
    menuStore.fetchMenuTree()
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.layout-container {
  height: 100vh;
  width: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.layout-header {
  background-color: #fff;
  color: #303133;
  padding: 0 20px;
  height: 60px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.logo-area {
  display: flex;
  align-items: center;
}

.logo-img {
  height: 32px;
  margin-right: 12px;
}

.system-title {
  font-size: 20px;
  font-weight: 600;
  color: #2c3e50;
}

.tenant-subtitle {
  font-size: 0.7em;
  font-weight: normal;
  color: #5a5e66;
  margin-left: 5px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 20px;
}

.action-icon {
  cursor: pointer;
  font-size: 20px;
  color: #5a5e66;
}

.action-icon:hover {
  color: var(--el-color-primary);
}

.action-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 0 10px;
  cursor: pointer;
}

.user-avatar-container {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.username {
  margin-left: 8px;
  font-size: 14px;
}

.mobile-menu-button {
  font-size: 24px;
}

.main-body-container {
  flex: 1;
  overflow: hidden;
}

.layout-sidebar {
  background-color: #fff;
  border-right: 1px solid #e4e7ed;
  transition: width 0.28s;
  position: relative;
}

.el-menu-vertical-custom:not(.el-menu--collapse) {
  width: 100%;
}

.el-menu-vertical-custom {
  border-right: none;
}

.el-menu-vertical-custom .el-menu-item.is-active {
  background-color: var(--el-color-primary-light-9) !important;
  color: var(--el-color-primary) !important;
}

.el-menu-vertical-custom .el-menu-item:hover {
  background-color: #ecf5ff;
}

.layout-sidebar .el-scrollbar {
  height: calc(100% - 40px);
}

.sidebar-collapse-button {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border-top: 1px solid #e4e7ed;
  background-color: #fff;
}

.sidebar-collapse-button:hover {
  background: linear-gradient(100deg, rgba(43, 151, 240, 0.05), rgba(143, 154, 255, 0.122));
}

.layout-main-content {
  padding: 0;
  background-color: #f0f2f5;
  height: 100%;
  width: 100%;
  flex: 1;
  overflow: hidden;
}

.main-content-scrollbar {
  height: 100%;
  width: 100%;
}

:deep(.el-scrollbar__view) {
  height: 100%;
  width: 100%;
}

:deep(.el-drawer__body) {
  padding: 0;
}

.notification-popover {
  padding: 0;
}

.popover-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #ebeef5;
  font-weight: 600;
  font-size: 14px;
}

.notification-list {
  display: flex;
  flex-direction: column;
}

.notification-item {
  padding: 12px 16px;
  border-bottom: 1px solid #f2f6fc;
  cursor: pointer;
  transition: background-color 0.2s;
}

.notification-item:hover {
  background-color: #f5f7fa;
}

.notification-item:last-child {
  border-bottom: none;
}

.item-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.item-content {
  font-size: 12px;
  color: #606266;
  line-height: 1.6;
  margin-bottom: 8px;
}

.item-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
  color: #909399;
}
</style>
