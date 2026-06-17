import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '../store/auth'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/auth/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/auth/Register.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: () => import('../views/auth/ForgotPassword.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/reset-password/:token',
    name: 'ResetPassword',
    component: () => import('../views/auth/ResetPassword.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/patients',
    name: 'Patients',
    component: () => import('../views/patients/PatientList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/patients/add',
    name: 'AddPatient',
    component: () => import('../views/patients/AddPatient.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/patients/:id',
    name: 'PatientDetails',
    component: () => import('../views/patients/PatientDetails.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/patients/:id/edit',
    name: 'EditPatient',
    component: () => import('../views/patients/EditPatient.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/appointments',
    name: 'Appointments',
    component: () => import('../views/appointments/AppointmentList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/appointments/add',
    name: 'AddAppointment',
    component: () => import('../views/appointments/AddAppointment.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/medications',
    name: 'Medications',
    component: () => import('../views/medications/MedicationList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/medications/add',
    name: 'AddMedication',
    component: () => import('../views/medications/AddMedication.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/prescriptions',
    name: 'Prescriptions',
    component: () => import('../views/prescriptions/PrescriptionList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/prescriptions/add',
    name: 'AddPrescription',
    component: () => import('../views/prescriptions/AddPrescription.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/bills',
    name: 'Bills',
    component: () => import('../views/bills/BillList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/bills/add',
    name: 'AddBill',
    component: () => import('../views/bills/AddBill.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/settings/Settings.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/users',
    name: 'Users',
    component: () => import('../views/users/UserList.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const isAuthenticated = authStore.isAuthenticated
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const requiresAdmin = to.matched.some(record => record.meta.requiresAdmin)
  const userRole = authStore.user?.role

  if (requiresAuth && !isAuthenticated) {
    next('/login')
  } else if (requiresAdmin && userRole !== 'admin') {
    next('/dashboard')
  } else {
    next()
  }
})

export default router