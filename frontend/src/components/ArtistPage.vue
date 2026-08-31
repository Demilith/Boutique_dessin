<template>
  <div :style="{'background-color': artist.theme_color || '#fff', 'padding':'20px'}">
    <div v-if="artist.header_image">
      <img :src="artist.header_image" alt="header" style="max-width:100%;height:200px;object-fit:cover" />
    </div>
    <h1>{{ artist.display_name || 'Artist' }}</h1>
    <div>
      <button @click="togglePreview">Toggle bio preview</button>
      <div v-if="preview" v-html="artist.bio"></div>
      <div v-else>{{ artist.bio }}</div>
    </div>
    <h2>Products</h2>
    <ul>
      <li v-for="p in artist.products" :key="p.id">
        <img v-if="p.image_url" :src="p.image_url" style="max-width:120px;max-height:120px" />
        <div>{{ p.title }} — €{{ (p.price_cents/100).toFixed(2) }}</div>
      </li>
    </ul>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  data() {
    return { artist: { products: [] }, preview: false }
  },
  async created() {
    const id = this.$route.params.id
    try {
      const res = await axios.get(`/api/artists/${id}/`)
      this.artist = res.data
    } catch (e) {
      console.error(e)
    }
  }
  ,methods: {
    togglePreview() { this.preview = !this.preview }
  }
}
</script>
