import axios from 'axios'

const API = axios.create({ baseURL: '/' })

export function setAuthToken(token) {
  if (token) {
    localStorage.setItem('access', token)
    API.defaults.headers.common['Authorization'] = `Bearer ${token}`
  } else {
    localStorage.removeItem('access')
    delete API.defaults.headers.common['Authorization']
  }
}

export async function register(data) {
  const res = await API.post('/api/register/', data)
  setAuthToken(res.data.access)
  return res.data
}

export async function login(credentials) {
  const res = await API.post('/api/token/', credentials)
  setAuthToken(res.data.access)
  return res.data
}

export function logout() {
  setAuthToken(null)
}

export default API
