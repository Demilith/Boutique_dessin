import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import ProductList from './components/ProductList.vue'
import ArtistPage from './components/ArtistPage.vue'
import Login from './components/Login.vue'
import Register from './components/Register.vue'
import Dashboard from './components/Dashboard.vue'
import CustomerOrders from './components/CustomerOrders.vue'
import { setAuthToken } from './auth'

const routes = [
  { path: '/', component: ProductList },
  { path: '/artist/:id', component: ArtistPage },
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  { path: '/dashboard', component: Dashboard },
  { path: '/orders', component: CustomerOrders },
]

const router = createRouter({ history: createWebHistory(), routes })

// Initialize auth token if present
setAuthToken(localStorage.getItem('access'))

createApp(App).use(router).mount('#app')
