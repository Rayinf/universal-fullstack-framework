<template>
  <el-config-provider :locale="zhCn">
    <MainLayout v-if="!isLoginPage" />
    <RouterView v-else />
  </el-config-provider>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import { useRoute } from 'vue-router'
import MainLayout from './layouts/MainLayout.vue'

const route = useRoute()
const isLoginPage = computed(() => route.path === '/login')
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html,
body {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  overflow-x: hidden;
  /* 防止水平滚动 */
}

#app {
  width: 100%;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  margin: 0;
  padding: 0;
  overflow: hidden;
  /* 防止溢出 */
}
</style>
