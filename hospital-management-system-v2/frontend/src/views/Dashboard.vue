<template>
  <div class="dashboard-container">
    <!-- Main Layout with Sidebar -->
    <el-container class="main-container">
      <!-- Sidebar Navigation -->
      <el-aside width="250px" class="sidebar">
        <div class="sidebar-header">
          <h3>Hospital System</h3>
        </div>
        
        <el-menu
          :default-active="activeMenu"
          class="sidebar-menu"
          router
          background-color="#001529"
          text-color="#fff"
          active-text-color="#409EFF"
          :collapse-transition="false"
        >
          <el-menu-item index="/dashboard">
            <el-icon><i-ep-home /></el-icon>
            <span>Dashboard</span>
          </el-menu-item>
          
          <el-menu-item index="/patients">
            <el-icon><i-ep-user /></el-icon>
            <span>Patients</span>
          </el-menu-item>
          
          <el-menu-item index="/appointments">
            <el-icon><i-ep-date /></el-icon>
            <span>Appointments</span>
          </el-menu-item>
          
          <el-menu-item index="/medications">
            <el-icon><i-ep-medical /></el-icon>
            <span>Medications</span>
          </el-menu-item>
          
          <el-menu-item index="/prescriptions">
            <el-icon><i-ep-document /></el-icon>
            <span>Prescriptions</span>
          </el-menu-item>
          
          <el-menu-item index="/bills">
            <el-icon><i-ep-money /></el-icon>
            <span>Billing</span>
          </el-menu-item>
          
          <el-menu-item index="/users" v-if="isAdmin">
            <el-icon><i-ep-setting /></el-icon>
            <span>Users</span>
          </el-menu-item>
          
          <el-menu-item index="/settings">
            <el-icon><i-ep-tools /></el-icon>
            <span>Settings</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      
      <!-- Main Content Area -->
      <el-container class="content-container">
        <!-- Top Header/Navigation Bar -->
        <el-header height="60px" class="main-header">
          <div class="header-left">
            <el-button 
              type="text" 
              class="menu-toggle"
              @click="toggleSidebar"
            >
              <el-icon><i-ep-menu /></el-icon>
            </el-button>
            <h2 class="page-title">{{ pageTitle }}</h2>
          </div>
          
          <div class="header-right">
            <!-- Notifications -->
            <el-dropdown>
              <el-button type="text" class="notification-btn">
                <el-icon><i-ep-bell /></el-icon>
                <span class="notification-badge" v-if="notifications.length > 0">{{ notifications.length }}</span>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item v-for="notification in notifications" :key="notification.id">
                    {{ notification.message }}
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            
            <!-- User Profile -->
            <el-dropdown @command="handleUserMenu">
              <div class="user-profile">
                <el-avatar :size="32" :src="userAvatar" />
                <span class="user-name">{{ currentUser?.full_name }}</span>
                <el-icon class="el-icon--right"><i-ep-arrow-down /></el-icon>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">View Profile</el-dropdown-item>
                  <el-dropdown-item command="settings">Settings</el-dropdown-item>
                  <el-dropdown-item divided command="logout">Logout</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>
        
        <!-- Dashboard Content -->
        <el-main class="dashboard-content">
          <!-- Welcome Section -->
          <div class="welcome-section">
            <h1>Welcome, {{ currentUser?.full_name }}!</h1>
            <p>Here's an overview of your hospital activities for today.</p>
          </div>
          
          <!-- Stats Cards -->
          <el-row :gutter="20" class="stats-row">
            <el-col :span="6">
              <el-card class="stat-card" shadow="hover">
                <div class="stat-content">
                  <div class="stat-icon blue">
                    <el-icon><i-ep-user /></el-icon>
                  </div>
                  <div class="stat-info">
                    <div class="stat-number">{{ todayPatients }}</div>
                    <div class="stat-label">Today's Patients</div>
                  </div>
                </div>
              </el-card>
            </el-col>
            
            <el-col :span="6">
              <el-card class="stat-card" shadow="hover">
                <div class="stat-content">
                  <div class="stat-icon green">
                    <el-icon><i-ep-date /></el-icon>
                  </div>
                  <div class="stat-info">
                    <div class="stat-number">{{ todayAppointments }}</div>
                    <div class="stat-label">Appointments</div>
                  </div>
                </div>
              </el-card>
            </el-col>
            
            <el-col :span="6">
              <el-card class="stat-card" shadow="hover">
                <div class="stat-content">
                  <div class="stat-icon purple">
                    <el-icon><i-ep-document /></el-icon>
                  </div>
                  <div class="stat-info">
                    <div class="stat-number">{{ newPrescriptions }}</div>
                    <div class="stat-label">New Prescriptions</div>
                  </div>
                </div>
              </el-card>
            </el-col>
            
            <el-col :span="6">
              <el-card class="stat-card" shadow="hover">
                <div class="stat-content">
                  <div class="stat-icon orange">
                    <el-icon><i-ep-money /></el-icon>
                  </div>
                  <div class="stat-info">
                    <div class="stat-number">${{ todayRevenue.toLocaleString() }}</div>
                    <div class="stat-label">Today's Revenue</div>
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>
          
          <!-- Charts Section -->
          <el-row :gutter="20" class="charts-row">
            <el-col :span="12">
              <el-card class="chart-card" shadow="hover">
                <template #header>
                  <div class="card-header">
                    <span>Monthly Patient Visits</span>
                  </div>
                </template>
                <div class="chart-container">
                  <canvas id="patientChart" width="400" height="200"></canvas>
                </div>
              </el-card>
            </el-col>
            
            <el-col :span="12">
              <el-card class="chart-card" shadow="hover">
                <template #header>
                  <div class="card-header">
                    <span>Department Distribution</span>
                  </div>
                </template>
                <div class="chart-container">
                  <canvas id="departmentChart" width="400" height="200"></canvas>
                </div>
              </el-card>
            </el-col>
          </el-row>
          
          <!-- Upcoming Appointments -->
          <el-row class="appointments-row">
            <el-col :span="24">
              <el-card class="appointments-card" shadow="hover">
                <template #header>
                  <div class="card-header">
                    <span>Upcoming Appointments</span>
                    <el-button type="primary" size="small" @click="$router.push('/appointments')">
                      View All
                    </el-button>
                  </div>
                </template>
                <el-table :data="upcomingAppointments" style="width: 100%">
                  <el-table-column prop="patient_name" label="Patient" min-width="180" />
                  <el-table-column prop="department" label="Department" width="120" />
                  <el-table-column prop="time" label="Time" width="100" />
                  <el-table-column prop="status" label="Status" width="100">
                    <template #default="scope">
                      <el-tag :type="getStatusType(scope.row.status)">
                        {{ scope.row.status }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column label="Actions" width="120" fixed="right">
                    <template #default="scope">
                      <el-button type="primary" size="small" @click="viewAppointment(scope.row.id)">
                        View
                      </el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </el-card>
            </el-col>
          </el-row>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../store/auth'
import { usePatientStore } from '../store/patients'
import Chart from 'chart.js/auto'

export default defineComponent({
  name: 'Dashboard',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const authStore = useAuthStore()
    const patientStore = usePatientStore()
    
    // Chart instances
    let patientChart: Chart | null = null
    let departmentChart: Chart | null = null
    
    // Computed properties
    const currentUser = computed(() => authStore.currentUser)
    const isAdmin = computed(() => authStore.isAdmin)
    const activeMenu = computed(() => route.path)
    
    // Dashboard data
    const todayPatients = ref(24)
    const todayAppointments = ref(18)
    const newPrescriptions = ref(12)
    const todayRevenue = ref(15680)
    
    const notifications = ref([
      { id: 1, message: 'New patient registered: Sarah Johnson' },
      { id: 2, message: 'Appointment reminder: John Smith at 3:00 PM' },
      { id: 3, message: 'Prescription ready for pickup: Michael Brown' }
    ])
    
    const upcomingAppointments = ref([
      { id: 1, patient_name: 'John Smith', department: 'Cardiology', time: '10:00 AM', status: 'confirmed' },
      { id: 2, patient_name: 'Emily Johnson', department: 'Pediatrics', time: '11:30 AM', status: 'pending' },
      { id: 3, patient_name: 'Michael Brown', department: 'Orthopedics', time: '2:00 PM', status: 'confirmed' },
      { id: 4, patient_name: 'Sarah Wilson', department: 'Dermatology', time: '3:30 PM', status: 'confirmed' },
      { id: 5, patient_name: 'David Taylor', department: 'Neurology', time: '4:15 PM', status: 'cancelled' }
    ])
    
    const userAvatar = computed(() => {
      // Generate avatar based on user's first and last name
      if (currentUser.value?.full_name) {
        const nameParts = currentUser.value.full_name.split(' ')
        return `https://ui-avatars.com/api/?name=${nameParts[0]}+${nameParts[1] || ''}&background=409EFF&color=fff`
      }
      return 'https://ui-avatars.com/api/?name=User&background=409EFF&color=fff'
    })
    
    const pageTitle = computed(() => {
      switch (route.path) {
        case '/dashboard': return 'Dashboard'
        case '/patients': return 'Patients Management'
        case '/appointments': return 'Appointments'
        case '/medications': return 'Medications'
        case '/prescriptions': return 'Prescriptions'
        case '/bills': return 'Billing'
        case '/users': return 'User Management'
        case '/settings': return 'Settings'
        default: return 'Dashboard'
      }
    })
    
    // Methods
    const toggleSidebar = () => {
      // Sidebar toggle logic would go here
      ElMessage.info('Sidebar toggle functionality')
    }
    
    const handleUserMenu = (command: string) => {
      switch (command) {
        case 'profile':
          ElMessage.info('View profile functionality')
          break
        case 'settings':
          router.push('/settings')
          break
        case 'logout':
          authStore.logout()
          router.push('/login')
          ElMessage.success('Logged out successfully')
          break
      }
    }
    
    const getStatusType = (status: string) => {
      switch (status.toLowerCase()) {
        case 'confirmed': return 'success'
        case 'pending': return 'warning'
        case 'cancelled': return 'danger'
        default: return 'info'
      }
    }
    
    const viewAppointment = (id: number) => {
      ElMessage.info(`View appointment ${id}`)
    }
    
    const initCharts = () => {
      // Patient visits chart
      const patientCtx = document.getElementById('patientChart') as HTMLCanvasElement
      if (patientCtx) {
        patientChart = new Chart(patientCtx, {
          type: 'line',
          data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            datasets: [{
              label: 'Patient Visits',
              data: [120, 150, 180, 140, 200, 250, 280, 300, 270, 220, 240, 260],
              borderColor: '#409EFF',
              backgroundColor: 'rgba(64, 158, 255, 0.1)',
              tension: 0.4,
              fill: true
            }]
          },
          options: {
            responsive: true,
            plugins: {
              legend: {
                display: false
              }
            },
            scales: {
              y: {
                beginAtZero: true
              }
            }
          }
        })
      }
      
      // Department distribution chart
      const deptCtx = document.getElementById('departmentChart') as HTMLCanvasElement
      if (deptCtx) {
        departmentChart = new Chart(deptCtx, {
          type: 'doughnut',
          data: {
            labels: ['Cardiology', 'Pediatrics', 'Orthopedics', 'Dermatology', 'Neurology', 'Other'],
            datasets: [{
              data: [300, 150, 200, 100, 120, 80],
              backgroundColor: [
                '#409EFF',
                '#67C23A',
                '#E6A23C',
                '#F56C6C',
                '#909399',
                '#C0C4CC'
              ]
            }]
          },
          options: {
            responsive: true,
            plugins: {
              legend: {
                position: 'right'
              }
            }
          }
        })
      }
    }
    
    onMounted(() => {
      // Check authentication
      authStore.checkAuth()
      if (!authStore.isAuthenticated) {
        router.push('/login')
        return
      }
      
      // Initialize charts
      initCharts()
      
      // Fetch initial data
      patientStore.fetchPatients()
    })
    
    return {
      currentUser,
      isAdmin,
      activeMenu,
      pageTitle,
      userAvatar,
      notifications,
      todayPatients,
      todayAppointments,
      newPrescriptions,
      todayRevenue,
      upcomingAppointments,
      toggleSidebar,
      handleUserMenu,
      getStatusType,
      viewAppointment
    }
  }
})
</script>

<style scoped>
.dashboard-container {
  height: 100vh;
  overflow: hidden;
}

.main-container {
  height: 100vh;
}

/* Sidebar Styles */
.sidebar {
  background-color: #001529;
  transition: width 0.3s;
}

.sidebar-header {
  padding: 20px;
  text-align: center;
  border-bottom: 1px solid #1890ff;
}

.sidebar-header h3 {
  color: #fff;
  margin: 0;
}

.sidebar-menu {
  border-right: none;
}

/* Header Styles */
.main-header {
  background-color: #fff;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.menu-toggle {
  color: #606266;
}

.page-title {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.notification-btn {
  position: relative;
  color: #606266;
}

.notification-badge {
  position: absolute;
  top: 0;
  right: 0;
  background-color: #f56c6c;
  color: #fff;
  border-radius: 50%;
  width: 18px;
  height: 18px;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 8px;
  transition: background-color 0.3s;
}

.user-profile:hover {
  background-color: #f5f7fa;
}

.user-name {
  font-size: 14px;
  color: #303133;
}

/* Main Content Styles */
.dashboard-content {
  padding: 20px;
  background-color: #f5f7fa;
  overflow-y: auto;
}

.welcome-section {
  margin-bottom: 24px;
}

.welcome-section h1 {
  margin: 0 0 8px 0;
  color: #303133;
}

.welcome-section p {
  margin: 0;
  color: #606266;
}

/* Stats Cards */
.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  height: 100%;
  border-radius: 12px;
  overflow: hidden;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: #fff;
}

.stat-icon.blue {
  background-color: #409EFF;
}

.stat-icon.green {
  background-color: #67C23A;
}

.stat-icon.purple {
  background-color: #909399;
}

.stat-icon.orange {
  background-color: #E6A23C;
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #606266;
}

/* Charts Section */
.charts-row {
  margin-bottom: 24px;
}

.chart-card {
  height: 100%;
  border-radius: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  padding: 20px 0;
}

/* Appointments Section */
.appointments-row {
  margin-bottom: 24px;
}

.appointments-card {
  border-radius: 12px;
}

/* Responsive Adjustments */
@media (max-width: 768px) {
  .sidebar {
    width: 0;
    overflow: hidden;
  }
  
  .sidebar.open {
    width: 250px;
  }
}
</style>