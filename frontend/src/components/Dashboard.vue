<template>
  <div>
    <h2>Your Dashboard</h2>
    <p>Manage your products and customize your public page.</p>
    <router-link to="/">Back to shop</router-link>

    <section>
      <h3>Your Profile</h3>
      <div>
        <label>Display name</label>
        <input v-model="profile.display_name" />
      </div>
      <div>
        <label>Bio</label>
        <textarea v-model="profile.bio"></textarea>
      </div>
      <div>
        <label>Theme color</label>
        <input v-model="profile.theme_color" type="color" />
      </div>
      <div>
        <label>Header image</label>
        <input type="file" @change="onHeaderFile" />
      </div>
      <button @click="saveProfile">Save profile</button>
    </section>

    <section>
      <h3>Your Products</h3>
      <button @click="creating = true">Create new product</button>
      <div v-if="creating">
        <product-form @saved="onSaved" />
      </div>
      <ul>
        <li v-for="p in products" :key="p.id">
          <strong>{{ p.title }}</strong> — €{{ (p.price_cents/100).toFixed(2) }} — stock: {{ p.stock }}
          <button @click="edit(p)">Edit</button>
          <button @click="retire(p)">Retire</button>
        </li>
      </ul>
      <div v-if="editing">
        <h4>Edit product</h4>
        <product-form :product="editing" @saved="onUpdated" />
      </div>
    </section>
    <section>
      <h3>Orders</h3>
      <ul>
        <li v-for="o in orders" :key="o.id">
          <div>Order #{{ o.id }} — €{{ (o.amount_cents/100).toFixed(2) }} — {{ o.fulfilled ? 'Fulfilled' : 'Pending' }} <span v-if="o.refunded">(Refunded)</span></div>
          <div v-if="o.invoice_url"><a :href="o.invoice_url" target="_blank">Download invoice</a></div>
          <button v-if="!o.refunded" @click="refund(o.id)">Refund</button>
        </li>
      </ul>
    </section>
  </div>
</template>

<script>
import API from '../auth'
import ProductForm from './ProductForm.vue'
import { setAuthTokens } from '../auth'

export default {
  name: 'Dashboard',
  components: { ProductForm },
  data() {
    return {
      products: [],
      orders: [],
      creating: false,
      editing: null,
      profile: { display_name: '', bio: '', theme_color: '#ffffff' },
      headerFile: null
    }
  },
  async created() {
    try {
      const res = await API.get('/api/my/products/')
      this.products = res.data
      const pr = await API.get('/api/my/profile/')
      this.profile = pr.data
      const or = await API.get('/api/my/orders/')
      this.orders = or.data
    } catch (e) {
      console.error(e)
    }
  },
  methods: {
    onSaved(prod) {
      this.products.unshift(prod)
      this.creating = false
    },
    onUpdated(prod) {
      const idx = this.products.findIndex(p => p.id === prod.id)
      if (idx !== -1) this.products.splice(idx, 1, prod)
      this.editing = null
    },
    edit(p) { this.editing = p },
    async retire(p) {
      try {
        await API.patch(`/api/products/${p.id}/`, { is_active: false })
        p.is_active = false
      } catch (e) { console.error(e) }
    },
    onHeaderFile(e) { this.headerFile = e.target.files[0] },
    async saveProfile() {
      try {
        const fd = new FormData()
        fd.append('display_name', this.profile.display_name)
        fd.append('bio', this.profile.bio)
        fd.append('theme_color', this.profile.theme_color)
        if (this.headerFile) fd.append('header_image', this.headerFile)
        const res = await API.put('/api/my/profile/', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
        this.profile = res.data
        alert('Profile saved')
      } catch (e) {
        console.error(e)
        alert('Failed to save profile')
      }
    }
    ,async refund(id) {
      if (!confirm('Initiate refund for this order?')) return
      try {
        await API.post(`/api/orders/${id}/refund/`)
        const idx = this.orders.findIndex(o => o.id === id)
        if (idx !== -1) this.orders[idx].refunded = true
        alert('Refund initiated')
      } catch (e) {
        console.error(e)
        alert('Refund failed')
      }
    }
  }
}
</script>
