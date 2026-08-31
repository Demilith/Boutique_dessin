<template>
  <div>
    <h2>Register</h2>
    <form @submit.prevent="doRegister">
      <div>
        <label>Username</label>
        <input v-model="form.username" />
      </div>
      <div>
        <label>Email</label>
        <input v-model="form.email" />
      </div>
      <div>
        <label>Password</label>
        <input type="password" v-model="form.password" />
      </div>
      <button type="submit">Register</button>
    </form>
  </div>
</template>

<script>
import { register } from '../auth'

export default {
  data() {
    return { form: { username: '', email: '', password: '' } }
  },
  methods: {
    async doRegister() {
      try {
        await register(this.form)
        this.$router.push('/dashboard')
      } catch (e) {
        alert('Registration failed')
      }
    }
  }
}
</script>
