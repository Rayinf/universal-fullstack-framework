<template>
  <el-container class="layout-container">
    <!-- 顶部 LOGO 和操作区域 -->
    <el-header class="layout-header">
      <div class="header-content">
        <div class="logo-area">
          <img src="@/assets/单LOGO.png" alt="系统LOGO" class="logo-img" v-if="!isMobile || sidebarCollapsed" />
          <span class="system-title">{{ systemTitle }} <span v-if="tenantName" class="tenant-subtitle">- {{ tenantName }}</span></span>
        </div>
        <div class="header-actions">
          <slot name="header-actions">
            <el-tooltip content="全屏" placement="bottom" v-if="!isMobile">
              <el-icon class="action-icon" @click="toggleFullScreen">
                <FullScreen />
              </el-icon>
            </el-tooltip>
          </slot>
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
          <el-icon class="action-icon mobile-menu-button" @click="toggleSidebarDrawer" v-if="isMobile">
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
            <slot name="menu-items"></slot>
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
            <slot name="menu-items"></slot>
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
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import {
  Fold, Expand, FullScreen, UserFilled, ArrowDown, Menu
} from '@element-plus/icons-vue';
import { useUserStore } from '../stores/userStore';

interface Props {
  systemTitle?: string;
}

const props = withDefaults(defineProps<Props>(), {
  systemTitle: 'MES管理系统'
});

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

const tenantName = computed(() => userStore.tenantName);

const sidebarCollapsed = ref(false);
const sidebarDrawerVisible = ref(false);
const isMobile = ref(window.innerWidth < 768);

const sidebarWidth = computed(() => (sidebarCollapsed.value ? '64px' : '220px'));
const activeMenu = computed(() => route.path);

const toggleSidebarCollapse = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value;
};

const toggleSidebarDrawer = () => {
  sidebarDrawerVisible.value = !sidebarDrawerVisible.value;
};

const handleResize = () => {
  isMobile.value = window.innerWidth < 768;
  if (!isMobile.value && sidebarDrawerVisible.value) {
    sidebarDrawerVisible.value = false;
  }
  if (isMobile.value) {
    sidebarCollapsed.value = false;
  }
};

const toggleFullScreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen();
  } else {
    if (document.exitFullscreen) {
      document.exitFullscreen();
    }
  }
};

const handleUserCommand = async (command: string) => {
  if (command === 'logout') {
    try {
      await userStore.logout();
      router.push({ name: 'Login' });
    } catch (error) {
      console.error('登出失败:', error);
    }
  } else if (command === 'profile') {
    router.push({ name: 'Profile' });
  }
};

const handleMobileMenuSelect = () => {
  sidebarDrawerVisible.value = false;
};

onMounted(() => {
  window.addEventListener('resize', handleResize);
  handleResize();

  if (!userStore.tenantName) {
    userStore.fetchTenantName();
  }
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize);
});
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
  box-shadow: 0 1px 4px rgba(0, 21, 41, .08);
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
</style>
