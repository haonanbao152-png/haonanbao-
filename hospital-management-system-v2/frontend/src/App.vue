<template>
  <div class="app-container">
    <el-config-provider namespace="ep" :locale="en">
      <router-view v-if="isAuthenticated" />
      <div v-else class="auth-container">
        <router-view />
      </div>
    </el-config-provider>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed } from 'vue'
import { useAuthStore } from './store/auth'
import { ElConfigProvider } from 'element-plus'
import en from 'element-plus/es/locale/lang/en'

export default defineComponent({
  name: 'App',
  components: {
    ElConfigProvider
  },
  setup() {
    const authStore = useAuthStore()
    const isAuthenticated = computed(() => authStore.isAuthenticated)

    return {
      isAuthenticated,
      en
    }
  }
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.app-container {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* 全局圆角样式 */
.el-card, .el-button, .el-input__wrapper, .el-select, .el-form-item__label, .el-table {
  border-radius: 8px !important;
}