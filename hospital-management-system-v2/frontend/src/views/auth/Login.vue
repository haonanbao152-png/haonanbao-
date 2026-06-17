<template>
  <div class="login-container">
    <el-card class="login-card" shadow="hover">
      <template #header>
        <div class="login-header">
          <h2>Hospital Management System</h2>
          <p>Please log in to your account</p>
        </div>
      </template>
      
      <el-form :model="loginForm" :rules="rules" ref="loginFormRef" label-position="top" class="login-form">
        <el-form-item label="Username" prop="username">
          <el-input 
            v-model="loginForm.username" 
            placeholder="Enter your username"
            :prefix-icon="User"
            autocomplete="username"
          />
        </el-form-item>
        
        <el-form-item label="Password" prop="password">
          <el-input 
            v-model="loginForm.password" 
            type="password" 
            placeholder="Enter your password"
            :prefix-icon="Lock"
            autocomplete="current-password"
            show-password
          />
        </el-form-item>
        
        <div class="form-actions">
          <el-checkbox v-model="rememberMe">Remember me</el-checkbox>
          <router-link to="/forgot-password" class="forgot-password">Forgot password?</router-link>
        </div>
        
        <el-button 
          type="primary" 
          class="login-button" 
          :loading="loading" 
          @click="handleLogin"
          :disabled="loading"
        >
          Log In
        </el-button>
        
        <div class="register-link">
          <span>Don't have an account?</span>
          <router-link to="/register">Register</router-link>
        </div>
      </el-form>
      
      <div v-if="error" class="error-message">
        <el-alert
          :title="error"
          type="error"
          show-icon
          :closable="false"
        />
      </div>
    </el-card>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { useAuthStore } from '../../store/auth'

export default defineComponent({
  name: 'Login',
  components: {
    User,
    Lock
  },
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    const loginFormRef = ref()
    
    const loginForm = reactive({
      username: '',
      password: ''
    })
    
    const rememberMe = ref(false)
    const loading = ref(false)
    const error = ref('')
    
    const rules = {
      username: [
        { required: true, message: 'Please enter your username', trigger: 'blur' }
      ],
      password: [
        { required: true, message: 'Please enter your password', trigger: 'blur' }
      ]
    }
    
    const handleLogin = async () => {
      if (!loginFormRef.value) return
      
      await loginFormRef.value.validate(async (valid: boolean) => {
        if (valid) {
          loading.value = true
          error.value = ''
          
          try {
            const success = await authStore.login(loginForm.username, loginForm.password)
            
            if (success) {
              ElMessage.success('Login successful')
              router.push('/dashboard')
            } else {
              error.value = authStore.error || 'Login failed'
              ElMessage.error('Login failed')
            }
          } catch (err: any) {
            error.value = err.message || 'Login failed'
            ElMessage.error('Login failed')
          } finally {
            loading.value = false
          }
        }
      })
    }
    
    return {
      loginForm,
      loginFormRef,
      rememberMe,
      loading,
      error,
      rules,
      handleLogin,
      User,
      Lock
    }
  }
})
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 420px;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 20px;
}

.login-header h2 {
  margin: 0;
  color: #1890ff;
  font-size: 24px;
  font-weight: 600;
}

.login-header p {
  margin: 8px 0 0;
  color: #606266;
  font-size: 14px;
}

.login-form {
  margin-top: 20px;
}

.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.forgot-password {
  color: #1890ff;
  text-decoration: none;
  font-size: 14px;
}

.forgot-password:hover {
  text-decoration: underline;
}

.login-button {
  width: 100%;
  height: 44px;
  font-size: 16px;
  border-radius: 8px;
  margin-bottom: 16px;
}

.register-link {
  text-align: center;
  font-size: 14px;
  color: #606266;
}

.register-link a {
  color: #1890ff;
  text-decoration: none;
  margin-left: 4px;
}

.register-link a:hover {
  text-decoration: underline;
}

.error-message {
  margin-top: 16px;
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
}

:deep(.el-button) {
  border-radius: 8px;
}

:deep(.el-card__header) {
  border-radius: 16px 16px 0 0;
  background-color: #fafafa;
}
</style>