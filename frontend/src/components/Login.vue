<template>
  <div>
    <h2>Login</h2>
    <form @submit.prevent="doLogin">
      <div>
        <label>Username</label>
        <input v-model="form.username" />
      </div>
      <div>
        <label>Password</label>
        <input type="password" v-model="form.password" />
      </div>
      <button type="submit">Login</button>
    </form>
  </div>
</template>

<script>
import { login } from '../auth'

export default {
  data() {
    return { form: { username: '', password: '' } }
  },
  methods: {
    async doLogin() {
      try {
        await login(this.form)
        this.$router.push('/dashboard')
      } catch (e) {
        alert('Login failed')
      }
    }
  }
}
</script>
