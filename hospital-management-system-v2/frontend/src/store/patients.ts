import { defineStore } from 'pinia'
import axios from 'axios'

interface Patient {
  id: number
  first_name: string
  last_name: string
  date_of_birth: string
  gender: string
  address: string
  phone_number: string
  email: string
  emergency_contact: string
  blood_type: string
  allergies: string
  created_at: string
  updated_at: string
}

interface PatientState {
  patients: Patient[]
  loading: boolean
  error: string | null
}

export const usePatientStore = defineStore('patients', {
  state: (): PatientState => ({
    patients: [],
    loading: false,
    error: null
  }),

  getters: {
    getPatientById: (state) => (id: number) => {
      return state.patients.find(patient => patient.id === id)
    },
    
    patientCount: (state) => state.patients.length
  },

  actions: {
    async fetchPatients() {
      this.loading = true
      this.error = null
      
      try {
        // Mock API call
        // const response = await axios.get('/api/patients')
        
        // Mock data
        const mockPatients: Patient[] = [
          {
            id: 1,
            first_name: 'John',
            last_name: 'Smith',
            date_of_birth: '1980-05-15',
            gender: 'Male',
            address: '123 Main St, New York',
            phone_number: '555-1234',
            email: 'john.smith@example.com',
            emergency_contact: 'Jane Smith (Wife) - 555-5678',
            blood_type: 'A+',
            allergies: 'Penicillin',
            created_at: '2024-01-15T10:30:00',
            updated_at: '2024-01-15T10:30:00'
          },
          {
            id: 2,
            first_name: 'Emily',
            last_name: 'Johnson',
            date_of_birth: '1992-08-22',
            gender: 'Female',
            address: '456 Oak Ave, Los Angeles',
            phone_number: '555-9876',
            email: 'emily.j@example.com',
            emergency_contact: 'Robert Johnson (Father) - 555-4321',
            blood_type: 'O-',
            allergies: 'None',
            created_at: '2024-01-10T14:20:00',
            updated_at: '2024-01-10T14:20:00'
          },
          {
            id: 3,
            first_name: 'Michael',
            last_name: 'Brown',
            date_of_birth: '1975-03-10',
            gender: 'Male',
            address: '789 Pine St, Chicago',
            phone_number: '555-5678',
            email: 'michael.b@example.com',
            emergency_contact: 'Lisa Brown (Spouse) - 555-8765',
            blood_type: 'B+',
            allergies: 'Sulfa',
            created_at: '2024-01-08T09:15:00',
            updated_at: '2024-01-08T09:15:00'
          }
        ]
        
        this.patients = mockPatients
      } catch (error: any) {
        this.error = error.message || 'Failed to fetch patients'
      } finally {
        this.loading = false
      }
    },

    async addPatient(patientData: Omit<Patient, 'id' | 'created_at' | 'updated_at'>) {
      this.loading = true
      this.error = null
      
      try {
        // Mock API call
        // const response = await axios.post('/api/patients', patientData)
        
        // Mock response
        const newPatient: Patient = {
          ...patientData,
          id: Date.now(),
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
        
        this.patients.push(newPatient)
        return newPatient
      } catch (error: any) {
        this.error = error.message || 'Failed to add patient'
        throw error
      } finally {
        this.loading = false
      }
    },

    async updatePatient(id: number, patientData: Partial<Patient>) {
      this.loading = true
      this.error = null
      
      try {
        // Mock API call
        // const response = await axios.put(`/api/patients/${id}`, patientData)
        
        const index = this.patients.findIndex(p => p.id === id)
        if (index !== -1) {
          this.patients[index] = {
            ...this.patients[index],
            ...patientData,
            updated_at: new Date().toISOString()
          }
          return this.patients[index]
        }
        throw new Error('Patient not found')
      } catch (error: any) {
        this.error = error.message || 'Failed to update patient'
        throw error
      } finally {
        this.loading = false
      }
    },

    async deletePatient(id: number) {
      this.loading = true
      this.error = null
      
      try {
        // Mock API call
        // await axios.delete(`/api/patients/${id}`)
        
        const index = this.patients.findIndex(p => p.id === id)
        if (index !== -1) {
          this.patients.splice(index, 1)
        } else {
          throw new Error('Patient not found')
        }
      } catch (error: any) {
        this.error = error.message || 'Failed to delete patient'
        throw error
      } finally {
        this.loading = false
      }
    }
  }
})