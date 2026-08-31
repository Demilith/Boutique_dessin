<template>
  <form @submit.prevent="submit">
    <div>
      <label>Title</label>
      <input v-model="form.title" />
    </div>
    <div>
      <label>Description</label>
      <textarea v-model="form.description"></textarea>
    </div>
    <div>
      <label>Price (EUR)</label>
      <input type="number" step="0.01" v-model.number="price" />
    </div>
    <div>
      <label>Stock</label>
      <input type="number" v-model.number="form.stock" />
    </div>
    <div>
      <label>Image</label>
      <input type="file" @change="onFile" />
      <div v-if="preview">
        <h4>Preview</h4>
        <img :src="preview" alt="preview" style="max-width:200px;max-height:200px" />
      </div>
    </div>
    <div>
      <label><input type="checkbox" v-model="form.is_new" /> New</label>
      <label><input type="checkbox" v-model="form.on_sale" /> On sale</label>
    </div>
    <button type="submit">Save</button>
  </form>
</template>

<script>
import API from '../auth'

export default {
  props: { product: { type: Object, default: null } },
  data() {
    return {
      form: {
        title: '', description: '', price_cents: 0, stock: 0, is_new: false, on_sale: false
      },
      file: null,
      price: 0
    }
  },
  created() {
    if (this.product) {
      this.form.title = this.product.title
      this.form.description = this.product.description
      this.form.price_cents = this.product.price_cents
      this.price = this.product.price_cents/100
      this.form.stock = this.product.stock
      this.form.is_new = this.product.is_new
      this.form.on_sale = this.product.on_sale
    }
  },
  methods: {
    onFile(e) { this.file = e.target.files[0]; this.createPreview() },
    createPreview() {
      if (this.file) {
        const reader = new FileReader()
        reader.onload = e => { this.preview = e.target.result }
        reader.readAsDataURL(this.file)
      } else if (this.product && this.product.image_url) {
        this.preview = this.product.image_url
      } else this.preview = null
    },
    async submit() {
      try {
        const formData = new FormData()
        formData.append('title', this.form.title)
        formData.append('description', this.form.description)
        formData.append('price_cents', Math.round((this.price || 0)*100))
        formData.append('stock', this.form.stock)
        formData.append('is_new', this.form.is_new)
        formData.append('on_sale', this.form.on_sale)
        if (this.file) formData.append('image', this.file)

        let res
        if (this.product && this.product.id) {
          res = await API.put(`/api/products/${this.product.id}/`, formData, { headers: { 'Content-Type': 'multipart/form-data' } })
        } else {
          res = await API.post('/api/products/', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
        }
        this.$emit('saved', res.data)
      } catch (e) {
        console.error(e)
        alert('Failed to save product')
      }
    }
  }
}
</script>
