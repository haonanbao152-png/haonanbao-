<template>
  <div class="patient-list-container">
    <!-- Header -->
    <div class="page-header">
      <h1>Patients Management</h1>
      <el-button type="primary" @click="$router.push('/patients/add')" class="add-patient-btn">
        <el-icon><i-ep-plus /></el-icon>
        Add Patient
      </el-button>
    </div>

    <!-- Search and Filter -->
    <el-card class="search-card" shadow="hover">
      <el-form :model="searchForm" layout="inline" class="search-form">
        <el-form-item label="Search">
          <el-input
            v-model="searchForm.keyword"
            placeholder="Search by name, phone, or email"
            :prefix-icon="Search"
            @input="handleSearch"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><i-ep-search /></el-icon>
            Search
          </el-button>
        </el-form-item>
        
        <el-form-item>
          <el-button @click="resetSearch">
            <el-icon><i-ep-refresh-right /></el-icon>
            Reset
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Patient Table -->
    <el-card class="table-card" shadow="hover">
      <el-table
        v-loading="loading"
        :data="filteredPatients"
        style="width: 100%"
        border
        stripe
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        
        <el-table-column prop="full_name" label="Patient Name" min-width="180" sortable>
          <template #default="scope">
            <div class="patient-name">
              <el-avatar :size="32" :src="getPatientAvatar(scope.row)" />
              <span>{{ scope.row.full_name }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="gender" label="Gender" width="100" />
        
        <el-table-column prop="date_of_birth" label="DOB" width="120" sortable>
          <template #default="scope">
            {{ formatDate(scope.row.date_of_birth) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="phone_number" label="Phone" width="150" />
        
        <el-table-column prop="email" label="Email" min-width="200" />
        
        <el-table-column prop="blood_type" label="Blood Type" width="100" />
        
        <el-table-column prop="created_at" label="Created" width="160" sortable>
          <template #default="scope">
            {{ formatDateTime(scope.row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="Actions" width="180" fixed="right">
          <template #default="scope">
            <el-button type="primary" size="small" @click="viewPatient(scope.row.id)">
              <el-icon><i-ep-view /></el-icon>
              View
            </el-button>
            
            <el-button type="success" size="small" @click="editPatient(scope.row.id)">
              <el-icon><i-ep-edit /></el-icon>
              Edit
            </el-button>
            
            <el-button type="danger" size="small" @click="deletePatient(scope.row)">
              <el-icon><i-ep-delete /></el-icon>
              Delete
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Pagination -->
    <div class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        :total="totalPatients"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- Delete Confirmation Dialog -->
    <el-dialog
      v-model="deleteDialogVisible"
      title="Delete Patient"
      width="400px"
      center
    >
      <div class="delete-dialog-content">
        <el-icon class="warning-icon"><i-ep-warning /></el-icon>
        <p>Are you sure you want to delete patient <strong>{{ selectedPatient?.full_name }}</strong>?</p>
        <p class="delete-warning">This action cannot be undone.</p>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="deleteDialogVisible = false">Cancel</el-button>
          <el-button type="danger" @click="confirmDelete" :loading="deleteLoading">
            Delete
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { usePatientStore } from '../../store/patients'

export default defineComponent({
  name: 'PatientList',
  components: {
    Search
  },
  setup() {
    const router = useRouter()
    const patientStore = usePatientStore()
    
    // State
    const loading = ref(false)
    const deleteLoading = ref(false)
    const deleteDialogVisible = ref(false)
    const selectedPatient = ref(null)
    const selectedPatients = ref([])
    
    // Pagination
    const currentPage = ref(1)
    const pageSize = ref(10)
    
    // Search form
    const searchForm = ref({
      keyword: ''
    })
    
    // Computed properties
    const patients = computed(() => patientStore.patients)
    const totalPatients = computed(() => patients.value.length)
    
    const filteredPatients = computed(() => {
      const keyword = searchForm.value.keyword.toLowerCase()
      if (!keyword) {
        return patients.value
      }
      
      return patients.value.filter(patient => 
        patient.full_name.toLowerCase().includes(keyword) ||
        patient.phone_number.toLowerCase().includes(keyword) ||
        patient.email.toLowerCase().includes(keyword)
      )
    })
    
    // Methods
    const fetchPatients = async () => {
      loading.value = true
      try {
        await patientStore.fetchPatients()
      } catch (error: any) {
        ElMessage.error('Failed to fetch patients: ' + error.message)
      } finally {
        loading.value = false
      }
    }
    
    const handleSearch = () => {
      currentPage.value = 1
      // Search is handled by the computed property
    }
    
    const resetSearch = () => {
      searchForm.value.keyword = ''
      currentPage.value = 1
    }
    
    const handleSelectionChange = (selection: any[]) => {
      selectedPatients.value = selection
    }
    
    const handleSizeChange = (newSize: number) => {
      pageSize.value = newSize
    }
    
    const handleCurrentChange = (newPage: number) => {
      currentPage.value = newPage
    }
    
    const viewPatient = (patientId: number) => {
      router.push(`/patients/${patientId}`)
    }
    
    const editPatient = (patientId: number) => {
      router.push(`/patients/${patientId}/edit`)
    }
    
    const deletePatient = (patient: any) => {
      selectedPatient.value = patient
      deleteDialogVisible.value = true
    }
    
    const confirmDelete = async () => {
      if (!selectedPatient.value) return
      
      deleteLoading.value = true
      try {
        await patientStore.deletePatient(selectedPatient.value.id)
        ElMessage.success('Patient deleted successfully')
        deleteDialogVisible.value = false
        selectedPatient.value = null
      } catch (error: any) {
        ElMessage.error('Failed to delete patient: ' + error.message)
      } finally {
        deleteLoading.value = false
      }
    }
    
    const getPatientAvatar = (patient: any) => {
      const nameParts = patient.full_name.split(' ')
      const firstName = nameParts[0] || ''
      const lastName = nameParts[1] || ''
      return `https://ui-avatars.com/api/?name=${firstName}+${lastName}&background=409EFF&color=fff`
    }
    
    const formatDate = (dateString: string) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }
    
    const formatDateTime = (dateString: string) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
    
    // Lifecycle
    onMounted(() => {
      fetchPatients()
    })
    
    return {
      loading,
      deleteLoading,
      deleteDialogVisible,
      selectedPatient,
      selectedPatients,
      currentPage,
      pageSize,
      searchForm,
      patients,
      totalPatients,
      filteredPatients,
      handleSearch,
      resetSearch,
      handleSelectionChange,
      handleSizeChange,
      handleCurrentChange,
      viewPatient,
      editPatient,
      deletePatient,
      confirmDelete,
      getPatientAvatar,
      formatDate,
      formatDateTime
    }
  }
})
</script>

<style scoped>
.patient-list-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h1 {
  margin: 0;
  color: #303133;
  font-size: 24px;
}

.add-patient-btn {
  border-radius: 8px;
}

.search-card {
  margin-bottom: 24px;
  border-radius: 12px;
}

.search-form {
  margin: 0;
}

.table-card {
  margin-bottom: 24px;
  border-radius: 12px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

.patient-name {
  display: flex;
  align-items: center;
  gap: 12px;
}

.patient-name span {
  font-weight: 500;
}

.delete-dialog-content {
  text-align: center;
  padding: 20px 0;
}

.warning-icon {
  font-size: 48px;
  color: #E6A23C;
  margin-bottom: 16px;
}

.delete-warning {
  color: #F56C6C;
  font-weight: 500;
  margin-top: 8px;
}

.dialog-footer {
  display: flex;
  justify-content: center;
  gap: 12px;
}

:deep(.el-button) {
  border-radius: 6px;
}

:deep(.el-table__header-wrapper th) {
  background-color: #fafafa;
  font-weight: 600;
}

:deep(.el-pagination .el-pager li) {
  border-radius: 4px;
}
</style>