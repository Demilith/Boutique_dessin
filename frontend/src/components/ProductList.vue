<template>
  <div>
    <h1>New & Featured</h1>
    <div v-if="products.length === 0">No products yet.</div>
    <div class="gallery">
      <div v-for="p in paged" :key="p.id" class="card">
        <img v-if="p.image_url" :src="p.image_url" alt="thumb" style="max-width:150px;max-height:150px" />
        <router-link :to="`/artist/${p.artist}`">{{ p.title }}</router-link>
        <div>{{ p.description }}</div>
        <div>
          <span v-if="p.is_new">New</span>
          <span v-if="p.on_sale">Sale</span>
        </div>
        <div>Price: €{{ (p.price_cents/100).toFixed(2) }}</div>
        <button @click.prevent="buy(p.id)">Buy</button>
      </div>
    </div>
    <div class="pagination">
      <button @click="prev" :disabled="page===1">Prev</button>
      <span>Page {{ page }} / {{ totalPages }}</span>
      <button @click="next" :disabled="page===totalPages">Next</button>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  data() {
    return { products: [], page: 1, perPage: 10 }
  },
  async created() {
    try {
      const res = await axios.get('/api/products/')
      this.products = res.data
    } catch (e) {
      console.error(e)
    }
  }
  ,
  methods: {
    async buy(id) {
      try {
        const res = await axios.post(`/api/stripe/checkout/${id}/`)
        if (res.data && res.data.url) {
          window.location.href = res.data.url
        }
      } catch (e) {
        console.error(e)
        alert('Unable to create checkout session')
      }
    }
  }
  ,computed: {
    totalPages() { return Math.max(1, Math.ceil(this.products.length / this.perPage)) },
    paged() { const start = (this.page-1)*this.perPage; return this.products.slice(start, start+this.perPage) }
  ,
  },
  watch: {
    products() { if (this.page > this.totalPages) this.page = this.totalPages }
  ,
  prev() { if (this.page>1) this.page-- },
  next() { if (this.page < this.totalPages) this.page++ }
}
</script>
