import axios from 'axios'

const API = axios.create({ baseURL: '/' })

function notifyAuthChange() {
  window.dispatchEvent(new Event('auth-changed'))
}

export function setAuthTokens(access, refresh = null) {
  if (access) {
    localStorage.setItem('access', access)
    API.defaults.headers.common['Authorization'] = `Bearer ${access}`

    if (refresh) {
      localStorage.setItem('refresh', refresh)
    }
  } else {
    localStorage.removeItem('access')
    localStorage.removeItem('refresh')
    delete API.defaults.headers.common['Authorization']
  }

  notifyAuthChange()
}

export async function register(data) {
  const res = await API.post('/api/register/', data)
  setAuthTokens(res.data.access, res.data.refresh)
  return res.data
}

export async function login(credentials) {
  const res = await API.post('/api/token/', credentials)
  setAuthTokens(res.data.access, res.data.refresh)
  return res.data
}

export function logout() {
  setAuthTokens(null)
}

export default API