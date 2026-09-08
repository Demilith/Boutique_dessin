<template>
  <div>
    <nav>
      <router-link to="/">Accueil</router-link>

      <template v-if="!isLoggedIn">
        <router-link to="/register">Inscription</router-link>
        <router-link to="/login">Connexion</router-link>
      </template>

      <template v-else>
        <router-link to="/dashboard">Tableau de bord</router-link>
        <router-link to="/orders">Mes commandes</router-link>
        <button @click="handleLogout">Déconnexion</button>
      </template>
    </nav>

    <router-view />
  </div>
</template>

<script>
import { logout } from './auth'

export default {
  data() {
    return {
      isLoggedIn: !!localStorage.getItem('access')
    }
  },

  mounted() {
    window.addEventListener('auth-changed', this.updateAuthState)
  },

  beforeUnmount() {
    window.removeEventListener('auth-changed', this.updateAuthState)
  },

  methods: {
    updateAuthState() {
      this.isLoggedIn = !!localStorage.getItem('access')
    },

    handleLogout() {
      logout()
      this.$router.push('/')
    }
  }
}
</script>

<style scoped>
nav {
  display: flex;
  gap: 16px;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #ddd;
}

nav a {
  text-decoration: none;
}

button {
  cursor: pointer;
}
</style>